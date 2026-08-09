/** Load categories available to the signed-in user. */

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export type Category = {
  id: number
  name: string
  description: string | null
  is_default: boolean
}

export async function getCategories(
  token: string,
  signal?: AbortSignal,
): Promise<Category[]> {
  const response = await fetch(`${API_URL}/categories/`, {
    headers: { Authorization: `Bearer ${token}` },
    signal,
  })

  if (!response.ok) {
    throw new Error('Categories could not be loaded.')
  }

  return (await response.json()) as Category[]
}
