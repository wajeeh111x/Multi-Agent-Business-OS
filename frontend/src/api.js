const API_BASE_URL = "http://127.0.0.1:8000";

export async function loginUser(email, password) {
  const formData = new URLSearchParams();

  formData.append("username", email);
  formData.append("password", password);

  const response = await fetch(
    `${API_BASE_URL}/auth/login`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Login failed"
    );
  }

  return data;
}

export async function registerUser(
  username,
  email,
  password
) {
  const response = await fetch(
    `${API_BASE_URL}/auth/register`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Registration failed"
    );
  }

  return data;
}

export async function getDashboard(datasetId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/business/datasets/${datasetId}/dashboard`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
        `Dashboard request failed: ${response.status}`
    );
  }

  return data;
}

export async function uploadDataset(file) {
  const token = localStorage.getItem("access_token");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/business/datasets/upload`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Dataset upload failed"
    );
  }

  return data;
}
export async function askDataset(datasetId, question) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/business/datasets/${datasetId}/ask?question=${encodeURIComponent(
      question
    )}`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "AI question failed"
    );
  }

  return data;
}