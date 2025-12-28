import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { logout, me, type MeResponse } from "../api/auth";
import { createProject, listProjects, type Project } from "../api/projects";

export default function ProjectsPage() {
  const nav = useNavigate();
  const [user, setUser] = useState<MeResponse | null>(null);

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [niche, setNiche] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      const u = await me();
      setUser(u);

      const list = await listProjects();
      setProjects(list);
    } catch (e: any) {
      setErr(e?.message || "Failed to load");
      // если токен протух/невалидный — выкидываем на логин
      logout();
      nav("/login");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setCreating(true);
    try {
      const p = await createProject({ name, niche, description });
      setProjects((prev) => [p, ...prev]);
      setName("");
      setNiche("");
      setDescription("");
    } catch (e: any) {
      setErr(e?.message || "Create failed");
    } finally {
      setCreating(false);
    }
  }

  function onLogout() {
    logout();
    nav("/login");
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Arial" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Projects</h2>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          {user && (
            <div style={{ opacity: 0.8 }}>
              {user.username} ({user.role})
            </div>
          )}
          <button onClick={onLogout} style={{ padding: "8px 12px", cursor: "pointer" }}>
            Logout
          </button>
        </div>
      </div>

      {err && (
        <div style={{ background: "#ffe5e5", padding: 10, borderRadius: 8, marginBottom: 12 }}>
          {err}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 12 }}>
          <h3>Create project</h3>
          <form onSubmit={onCreate} style={{ display: "grid", gap: 10 }}>
            <input
              placeholder="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{ padding: 10 }}
            />
            <input
              placeholder="Niche"
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              style={{ padding: 10 }}
            />
            <textarea
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{ padding: 10, minHeight: 80 }}
            />
            <button disabled={creating} style={{ padding: 12, cursor: "pointer" }}>
              {creating ? "Creating..." : "Create"}
            </button>
          </form>
        </div>

        <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 12 }}>
          <h3>List</h3>
          {loading ? (
            <div>Loading...</div>
          ) : projects.length === 0 ? (
            <div style={{ opacity: 0.7 }}>No projects yet</div>
          ) : (
            <div style={{ display: "grid", gap: 10 }}>
              {projects.map((p) => (
                <div key={p.id} style={{ border: "1px solid #eee", borderRadius: 10, padding: 12 }}>
                  <div style={{ fontWeight: 700 }}>{p.name}</div>
                  <div style={{ opacity: 0.8, marginTop: 4 }}>{p.niche}</div>
                  <div style={{ marginTop: 8 }}>{p.description}</div>
                  <div style={{ opacity: 0.65, marginTop: 8, fontSize: 12 }}>
                    status: {p.status} • id: {p.id}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
