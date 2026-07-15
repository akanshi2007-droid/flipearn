/**
 * api.js — Central place for all backend communication.
 *
 * Every fetch call goes through here.
 * If the backend URL ever changes, you only update it in ONE place.
 *
 * Backend runs on: http://localhost:8000
 * Frontend runs on: http://localhost:5173
 */

const BASE_URL = "http://localhost:8000";

/**
 * Fetch the 4 stat card numbers shown on the dashboard.
 * No login required — this is a public endpoint.
 */
export async function fetchDashboardStats() {
  const res = await fetch(`${BASE_URL}/api/dashboard/public-stats`);
  if (!res.ok) throw new Error("Failed to fetch dashboard stats");
  return res.json();
  // Returns: { total_listings, active_listings, total_users, total_revenue }
}

/**
 * Fetch all active listings shown in the table.
 * No login required — public marketplace data.
 */
export async function fetchListings() {
  const res = await fetch(`${BASE_URL}/api/listings`);
  if (!res.ok) throw new Error("Failed to fetch listings");
  return res.json();
  // Returns: array of listing objects
}
