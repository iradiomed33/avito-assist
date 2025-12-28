import { api } from "./client";

export type Project = {
  id: number;
  name: string;
  niche: string;
  description: string;
  status: string;
  created_at: string;
};

export async function listProjects() {
  return api<Project[]>("/api/v1/projects", { auth: true });
}

export async function createProject(payload: { name: string; niche?: string; description?: string }) {
  return api<Project>("/api/v1/projects", {
    method: "POST",
    auth: true,
    body: payload,
  });
}
