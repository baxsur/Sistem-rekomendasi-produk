export const login = async (data) => {
  const response = await fetch("/api/login", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return response;
};

export const logout = async () => {
  return await fetch("/api/logout", {
    method: "POST",
    credentials: "include",
  });
};

export const getMe = async () => {
  return await fetch("/api/me", {
    credentials: "include",
  });
};