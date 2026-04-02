import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, test, expect, beforeEach, afterEach, vi } from "vitest";
import Login from "../Login";
import { BrowserRouter } from "react-router-dom";

// ✅ Mock navigate
const mockedNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockedNavigate,
  };
});

// ✅ Mock fetch
global.fetch = vi.fn();

function renderComponent() {
  return render(
    <BrowserRouter>
      <Login />
    </BrowserRouter>
  );
}

describe("Login Component", () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup(); // ✅ prevents multiple render issue
  });

  // ✅ 1. Render test
  test("renders login form", () => {
    renderComponent();

    expect(screen.getByText("LOGIN IN")).toBeInTheDocument();
    expect(screen.getByText("USERNAME")).toBeInTheDocument();
    expect(screen.getByText("PASSWORD")).toBeInTheDocument();
  });

  // ✅ 2. Empty validation
  test("shows error if fields are empty", () => {
    renderComponent();

    fireEvent.click(screen.getByDisplayValue("LOG IN"));

    expect(screen.getByText("fill the form completely")).toBeInTheDocument();
  });

  // ✅ 3. Invalid username
  test("shows error for short username", () => {
    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "ab" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "1234" },
    });

    fireEvent.click(screen.getByDisplayValue("LOG IN"));

    expect(screen.getByText("invalid user")).toBeInTheDocument();
  });

  // ✅ 4. Successful login
  test("logs in successfully", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        identity: "123",
        username: "testuser",
        usermail: "test@mail.com",
        session: "abc123"
      }),
    });

    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "123456" },
    });

    fireEvent.click(screen.getByDisplayValue("LOG IN"));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalled();
    });

    expect(localStorage.getItem("username")).toBe("testuser");
    expect(sessionStorage.getItem("session_id")).toBe("abc123");
  });

  // ✅ 5. API failure
  test("shows error on failed login", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      statusText: "Unauthorized",
      json: async () => ({ detail: "Invalid credentials" }),
    });

    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "wrongpass" },
    });

    fireEvent.click(screen.getByDisplayValue("LOG IN"));

    await waitFor(() => {
      expect(
        screen.getByText("Unauthorized:Invalid credentials")
      ).toBeInTheDocument();
    });
  });

  // ✅ 6. Forget password navigation
  test("navigates to forget password", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        usrmail: "test@mail.com",
        reset_key: "key123"
      }),
    });

    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.click(screen.getByText("forget password"));

    await waitFor(() => {
      expect(mockedNavigate).toHaveBeenCalledWith("/forget_password", {
        state: {
          Email: "test@mail.com",
          reset_key: "key123"
        }
      });
    });
  });

});