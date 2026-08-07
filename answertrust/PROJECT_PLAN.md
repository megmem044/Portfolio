# AnswerTrust Project Roadmap

AnswerTrust will be built in 12 small phases. Each phase adds one clear part of
the product and includes a check before work continues.

The finished application will evaluate an AI-generated answer against a
question and reference, score five quality areas, and recommend `PUBLISH`,
`REVIEW`, or `REJECT`.

## 1. Project setup

Create the folder structure, README, MIT licence, dependency list, shared
settings, and basic data structures.

**Check:** Confirm the required files exist and Python can import the project.

## 2. Input validation

Define the information used in an evaluation and reject empty, meaningless, or
excessively long input with clear messages.

**Check:** Test valid input, missing fields, whitespace, meaningless text, and
length limits.

## 3. Five quality checks

Build separate checks for:

- **Relevance:** Does the answer respond to the question?
- **Source support:** Are its claims supported by the supplied reference?
- **Completeness:** Does it address the full request?
- **Clarity:** Is it readable, focused, and well organized?
- **Uncertainty:** Does its confidence match the available evidence?

Each check will return a score, explanation, and specific concerns.

**Check:** Use self-authored examples covering relevant, irrelevant, supported,
unsupported, incomplete, unclear, and overly confident answers.

## 4. Scoring and decisions

Combine the five scores into an overall score from 0 to 100. Use visible rules
to recommend `PUBLISH`, `REVIEW`, or `REJECT`, identify the main concern, and
suggest the next action.

**Check:** Test score calculations, exact decision boundaries, and serious
concerns that must prevent publication.

## 5. Evaluation history

Use SQLite, Python's built-in local database, to save evaluations and retrieve
them by decision, score, or problem type.

**Check:** Test database creation, saving, reading, filtering, empty history,
and database errors using temporary test files.

## 6. Main application page

Build the Streamlit Evaluate Answer page. Show the decision and overall score
first, followed by quality scores, explanation, concerns, next action, and
evaluation time.

**Check:** Try valid and invalid submissions, confirm results are saved once,
and verify that the application starts successfully.

## 7. Optional local AI model

Add a small local model to improve short explanations and compare a basic
prompt with a more detailed safety-focused prompt. The rule-based evaluator
will remain the official decision maker.

**Check:** Use simulated model responses to test success, missing model files,
bad output, and model failure. The application must still work without the
model.

## 8. Labelled example set

Write at least 20 original examples across five groups: supported, partially
supported, unsupported, irrelevant, and insufficient reference information.
Each example will include its expected decision and a short reason.

**Check:** Confirm the file is valid, IDs are unique, required fields are
present, and each group contains at least four examples.

## 9. Offline experiments

Run the labelled examples through the evaluator and both model prompts. Measure
decision accuracy, unsupported-answer detection, false-publish rate, review
rate, processing time, and disagreement between the evaluator and model.

The main safety measure is **false-publish rate**: how often an unsafe or
unsupported answer is incorrectly recommended for publication.

**Check:** Verify sample calculations by hand and save the actual results as
CSV tables. Missing model results must be marked unavailable, never invented.

## 10. History and dashboard pages

Build an Evaluation History page with filters and a Quality Dashboard showing
decision counts, average scores, speed, common concerns, experiment results,
and prompt comparison.

**Check:** Compare displayed values with the saved data and test empty,
single-record, and populated views.

## 11. Complete product testing

Test the full workflow with supported, partial, unsupported, irrelevant, and
insufficient-reference answers. Also test model and database failures, remove
unused code, and improve unclear messages.

**Check:** Run all automated tests, open every Streamlit page, run the full
experiment, and confirm the main evaluator works without internet access.

## 12. Portfolio preparation

Complete the README with screenshots, architecture, actual experiment results,
setup instructions, limitations, privacy and licensing notes, resume bullets,
and a short interview explanation.

**Check:** Follow the setup instructions on a clean computer, rerun every
reported test and experiment, verify links, and check that no private or
generated files are included.

## Completion checklist

The project is complete when:

- All three Streamlit pages work locally with Python 3.11.
- The evaluator works when the optional model is unavailable.
- At least 20 self-authored labelled examples are included.
- Real experiment results and false-publish rate are reported.
- SQLite history and filters work.
- All automated tests pass.
- No paid service, API key, copied Quora content, model files, local database,
  virtual environment, cache, or private file is committed.

AnswerTrust checks whether an answer is supported by the supplied reference. It
does not determine whether a statement is universally true.
