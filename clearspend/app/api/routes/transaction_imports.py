"""Stream, stage, review, commit, and reconcile CSV imports."""
import hashlib, io, json
from datetime import datetime, timezone
from decimal import Decimal
from time import perf_counter
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, get_db
from app.api.routes.transactions import categorize_merchant, find_category
from app.models.transaction import Transaction
from app.models.transaction_import import TransactionImport, TransactionImportRow
from app.models.user import User
from app.schemas.transaction_import import ImportCommit, ImportCreate, ImportMapping, ImportPreset, ImportRead, ImportRowDecision, ReconciliationRead
from app.services.transaction_imports import MAX_FILE_BYTES, STAGING_BATCH_SIZE, iter_classified_rows, iter_csv, read_csv

router=APIRouter(prefix="/imports",tags=["imports"])
PRESETS=(ImportPreset(id="clearspend",name="ClearSpend standard",mapping=ImportMapping()),ImportPreset(id="debit-credit",name="Debit and credit columns",mapping=ImportMapping(amount=None,debit="debit",credit="credit")),ImportPreset(id="description-posted",name="Description and posted date",mapping=ImportMapping(date="posted",merchant="description")))

def owned_import(import_id:int,owner_id:int,db:Session,lock:bool=False):
 q=db.query(TransactionImport).filter(TransactionImport.id==import_id,TransactionImport.owner_id==owner_id); result=(q.with_for_update() if lock else q).one_or_none()
 if result is None: raise HTTPException(404,"import not found")
 return result

def page_data(item:TransactionImport,db:Session,page:int=1,page_size:int=100,status_filter:str|None=None):
 q=db.query(TransactionImportRow).filter(TransactionImportRow.import_id==item.id)
 if status_filter:q=q.filter(TransactionImportRow.status==status_filter)
 total=q.count(); rows=q.order_by(TransactionImportRow.row_number).offset((page-1)*page_size).limit(page_size).all()
 return {"id":item.id,"filename":item.filename,"source":item.source,"state":item.state,"input_count":item.input_count,"imported_count":item.imported_count,"duplicate_count":item.duplicate_count,"invalid_count":item.invalid_count,"rejected_count":item.rejected_count,"created_at":item.created_at,"committed_at":item.committed_at,"parsing_ms":item.parsing_ms,"validation_ms":item.validation_ms,"staging_ms":item.staging_ms,"commit_ms":item.commit_ms,"rows_per_second":item.rows_per_second,"peak_memory_bytes":item.peak_memory_bytes,"rows":rows,"row_total":total,"page":page,"page_size":page_size}

def stage(filename,source,file_hash,raw_rows,mapping,owner,db):
 started=perf_counter(); item=TransactionImport(owner=owner,filename=filename.strip(),source=source.strip(),state="validating",file_hash=file_hash);db.add(item);db.flush();count=duplicates=invalid=0;batch=[];batch_bytes=peak_batch_bytes=0
 try:
  for parsed in iter_classified_rows(raw_rows,mapping,owner.id,db):
   count+=1;duplicates+=parsed["status"]=="exact_duplicate";invalid+=parsed["status"]=="invalid";batch.append({"import_id":item.id,**parsed});batch_bytes+=len(json.dumps(parsed["raw_values"],default=str).encode())+512;peak_batch_bytes=max(peak_batch_bytes,batch_bytes)
   if len(batch)>=STAGING_BATCH_SIZE:db.bulk_insert_mappings(TransactionImportRow,batch);batch.clear();batch_bytes=0
  if batch:db.bulk_insert_mappings(TransactionImportRow,batch)
 except ValueError:db.rollback();raise
 elapsed=perf_counter()-started;item.state="ready";item.input_count=count;item.duplicate_count=duplicates;item.invalid_count=invalid;item.validation_ms=round(elapsed*1000);item.staging_ms=round(elapsed*1000);item.rows_per_second=Decimal(str(round(count/max(elapsed,.000001),2)));item.peak_memory_bytes=peak_batch_bytes;db.commit();db.refresh(item);return item

@router.get("/presets",response_model=list[ImportPreset])
def presets(current_user:User=Depends(get_current_user)):return PRESETS

@router.post("/",response_model=ImportRead,status_code=201)
def create_import(payload:ImportCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
 try:item=stage(payload.filename,payload.source,hashlib.sha256(payload.csv_content.encode()).hexdigest(),iter(read_csv(payload.csv_content)),payload.mapping,current_user,db)
 except ValueError as error:raise HTTPException(422,str(error)) from error
 return page_data(item,db)

@router.post("/upload",response_model=ImportRead,status_code=201)
def upload_import(file:UploadFile=File(...),mapping:str=Form(...),source:str=Form("uploaded-csv"),db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
 file.file.seek(0,2);size=file.file.tell();file.file.seek(0)
 if size>MAX_FILE_BYTES:raise HTTPException(413,"file exceeds the 5 MiB limit")
 if not file.filename or not file.filename.lower().endswith(".csv"):raise HTTPException(422,"a CSV filename is required")
 try:mapped=ImportMapping.model_validate(json.loads(mapping))
 except (json.JSONDecodeError,ValueError) as error:raise HTTPException(422,"mapping is not valid JSON") from error
 digest=hashlib.sha256()
 while chunk:=file.file.read(1024*1024):digest.update(chunk)
 file.file.seek(0);stream=io.TextIOWrapper(file.file,encoding="utf-8-sig",newline="")
 try:item=stage(file.filename,source,digest.hexdigest(),iter_csv(stream),mapped,current_user,db)
 except (UnicodeDecodeError,ValueError) as error:raise HTTPException(422,str(error)) from error
 finally:stream.detach()
 return page_data(item,db)

@router.get("/{import_id}",response_model=ImportRead)
def get_import(import_id:int,page:int=Query(1,ge=1),page_size:int=Query(100,ge=1,le=500),status_filter:str|None=None,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):return page_data(owned_import(import_id,current_user.id,db),db,page,page_size,status_filter)

@router.patch("/{import_id}/rows/{row_id}",response_model=ImportRead)
def review_row(import_id:int,row_id:int,review:ImportRowDecision,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
 item=owned_import(import_id,current_user.id,db)
 if item.state!="ready":raise HTTPException(409,"only ready imports can be reviewed")
 row=db.query(TransactionImportRow).filter(TransactionImportRow.id==row_id,TransactionImportRow.import_id==import_id).one_or_none()
 if row is None:raise HTTPException(404,"import row not found")
 if row.status!="possible_duplicate":raise HTTPException(422,"only possible duplicates require review")
 row.review_decision=review.decision;db.commit();db.refresh(item);return page_data(item,db)

@router.post("/{import_id}/commit",response_model=ReconciliationRead)
def commit_import(import_id:int,options:ImportCommit,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
 item=owned_import(import_id,current_user.id,db,True)
 if item.state=="committed":return reconciliation(item,db)
 started=perf_counter()
 try:
  for row in db.query(TransactionImportRow).filter(TransactionImportRow.import_id==import_id).order_by(TransactionImportRow.id).yield_per(STAGING_BATCH_SIZE):
   if row.status=="possible_duplicate" and (row.review_decision=="reject" or (row.review_decision is None and options.possible_duplicates=="reject")):row.status="rejected"
   if row.status not in {"new","possible_duplicate"}:continue
   category=find_category(categorize_merchant(row.merchant,current_user.id,db),current_user.id,db);saved=Transaction(owner=current_user,amount=row.amount,merchant=row.merchant,date=row.date,category_record=category,fingerprint=row.fingerprint);db.add(saved);db.flush();row.transaction=saved;row.status="imported"
  db.flush();counts=dict(db.query(TransactionImportRow.status,func.count(TransactionImportRow.id)).filter(TransactionImportRow.import_id==import_id).group_by(TransactionImportRow.status).all());item.state="committed";item.committed_at=datetime.now(timezone.utc);item.commit_ms=round((perf_counter()-started)*1000);item.imported_count=counts.get("imported",0);item.duplicate_count=counts.get("exact_duplicate",0);item.invalid_count=counts.get("invalid",0);item.rejected_count=counts.get("rejected",0);db.commit()
 except IntegrityError as error:db.rollback();raise HTTPException(409,"a concurrent import created a duplicate; retry the import") from error
 db.refresh(item);return reconciliation(item,db)

@router.get("/{import_id}/reconciliation",response_model=ReconciliationRead)
def get_reconciliation(import_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):return reconciliation(owned_import(import_id,current_user.id,db),db)

def reconciliation(item,db):
 accounted=item.imported_count+item.duplicate_count+item.invalid_count+item.rejected_count;accepted=db.query(func.coalesce(func.sum(TransactionImportRow.amount),0)).filter(TransactionImportRow.import_id==item.id,TransactionImportRow.status=="imported").scalar();saved=db.query(func.coalesce(func.sum(Transaction.amount),0)).join(TransactionImportRow,TransactionImportRow.transaction_id==Transaction.id).filter(TransactionImportRow.import_id==item.id).scalar()
 return {"import_id":item.id,"state":item.state,"input_count":item.input_count,"imported_count":item.imported_count,"duplicate_count":item.duplicate_count,"invalid_count":item.invalid_count,"rejected_count":item.rejected_count,"accounted_count":accounted,"reconciled":accounted==item.input_count and Decimal(saved)==Decimal(accepted),"accepted_total":Decimal(accepted),"saved_total":Decimal(saved)}
