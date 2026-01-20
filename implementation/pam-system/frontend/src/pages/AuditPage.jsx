import React, { useEffect, useMemo, useState } from "react";
import { apiFetch, getErrorMessage } from "../api";
import { useAuth } from "../App";
import { useToast } from "../components/ToastProvider";

const DEFAULT_PAGE_SIZE = 10;

function formatTimestamp(value) {
  try {
    return new Date(value).toLocaleString();
  } catch (err) {
    return value;
  }
}

export default function AuditPage() {
  const { user } = useAuth();
  const { addToast } = useToast();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("");
  const [resourceFilter, setResourceFilter] = useState("");
  const [sortKey, setSortKey] = useState("ts_desc");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const load = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    params.set("page", page.toString());
    params.set("page_size", pageSize.toString());
    if (search.trim()) {
      params.set("search", search.trim());
    }
    if (actionFilter) {
      params.set("action", actionFilter);
    }
    if (resourceFilter) {
      params.set("resource_type", resourceFilter);
    }
    if (sortKey) {
      params.set("sort", sortKey);
    }
    const response = await apiFetch(`/audit?${params.toString()}`);
    if (response.ok) {
      const data = await response.json();
      setEvents(data.items);
      setTotalPages(data.total_pages);
      setTotalItems(data.total);
    } else {
      addToast(await getErrorMessage(response), "error");
    }
    setLoading(false);
  };

  useEffect(() => {
    if (user?.is_admin) {
      load();
    }
  }, [user?.is_admin, search, actionFilter, resourceFilter, sortKey, page, pageSize]);

  const currentPage = Math.min(page, totalPages);
  const pageData = events;

  const actions = useMemo(() => {
    const values = new Set(events.map((event) => event.action));
    if (actionFilter) {
      values.add(actionFilter);
    }
    return [...values].sort();
  }, [events, actionFilter]);

  const resources = useMemo(() => {
    const values = new Set(events.map((event) => event.resource_type));
    if (resourceFilter) {
      values.add(resourceFilter);
    }
    return [...values].sort();
  }, [events, resourceFilter]);

  if (!user?.is_admin) {
    return <div className="notice">Admin access required.</div>;
  }

  return (
    <div>
      <div className="card">
        <h2>Audit Logs</h2>
        <div style={{ display: "grid", gap: 10, gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))" }}>
          <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder="Search" />
          <select value={actionFilter} onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}>
            <option value="">All actions</option>
            {actions.map((action) => (
              <option key={action} value={action}>{action}</option>
            ))}
          </select>
          <select value={resourceFilter} onChange={(e) => { setResourceFilter(e.target.value); setPage(1); }}>
            <option value="">All resources</option>
            {resources.map((resource) => (
              <option key={resource} value={resource}>{resource}</option>
            ))}
          </select>
          <select value={sortKey} onChange={(e) => { setSortKey(e.target.value); setPage(1); }}>
            <option value="ts_desc">Newest first</option>
            <option value="ts_asc">Oldest first</option>
            <option value="action_asc">Action A-Z</option>
            <option value="action_desc">Action Z-A</option>
            <option value="resource_asc">Resource A-Z</option>
            <option value="resource_desc">Resource Z-A</option>
          </select>
          <select value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
            <option value={10}>10 / page</option>
            <option value={20}>20 / page</option>
            <option value={50}>50 / page</option>
          </select>
          <button className="secondary" onClick={load} disabled={loading}>{loading ? "Loading..." : "Refresh"}</button>
        </div>
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Resource</th>
              <th>ID</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            {pageData.map((event) => (
              <tr key={event.id}>
                <td>{formatTimestamp(event.ts)}</td>
                <td>{event.actor_id ?? "-"}</td>
                <td>{event.action}</td>
                <td>{event.resource_type}</td>
                <td>{event.resource_id}</td>
                <td>{event.ip ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {pageData.length === 0 && <div className="notice">No audit events match the filters.</div>}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
          <span>Page {currentPage} of {totalPages} (Total {totalItems})</span>
          <div style={{ display: "flex", gap: 8 }}>
            <button className="secondary" onClick={() => setPage(Math.max(1, currentPage - 1))} disabled={currentPage === 1}>
              Previous
            </button>
            <button className="secondary" onClick={() => setPage(Math.min(totalPages, currentPage + 1))} disabled={currentPage === totalPages}>
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
