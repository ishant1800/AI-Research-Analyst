/**
 * API configuration for AI Research Analyst
 * In local development: defaults to empty string so requests go to Vite proxy (/api)
 * In production (e.g. Vercel): uses VITE_API_BASE_URL pointing to the Render backend service
 */
export const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? 'https://ai-research-analyst-ae81.onrender.com' : '');
