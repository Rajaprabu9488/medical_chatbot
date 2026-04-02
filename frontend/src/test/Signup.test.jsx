import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";
import { describe, test, expect, beforeEach, afterEach, vi } from "vitest";
import Signup from "../Signup";
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
      <Signup />
    </BrowserRouter>
  );
}

describe("Signup Component", () => {

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  // ✅ 1. Render Test
  test("renders signup form", () => {
    renderComponent();

    expect(screen.getByText("CREATE THE ACCOUNT")).toBeInTheDocument();
    expect(screen.getByLabelText("USERNAME")).toBeInTheDocument();
    expect(screen.getByLabelText("E-MAIL")).toBeInTheDocument();
    expect(screen.getByLabelText("PASSWORD")).toBeInTheDocument();
    expect(screen.getByLabelText("CONFIRM PASSWORD")).toBeInTheDocument();
  });

  // ✅ 2. Empty Validation
  test("shows error if fields are empty", () => {
    renderComponent();

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    expect(screen.getByText("fill the form completely")).toBeInTheDocument();
  });

  // ✅ 3. Username validation
  test("invalid username length", () => {
    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "ab" },
    });

    fireEvent.change(screen.getByLabelText("E-MAIL"), {
      target: { value: "test@mail.com" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.change(screen.getByLabelText("CONFIRM PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    expect(
      screen.getByText("username must be more than 3 charaters")
    ).toBeInTheDocument();
  });

  // ✅ 4. Email validation
  test("invalid email format", () => {
    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("E-MAIL"), {
      target: { value: "wrongemail" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.change(screen.getByLabelText("CONFIRM PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    expect(screen.getByText("Invalid E-mail id")).toBeInTheDocument();
  });

  // ✅ 5. Password mismatch
  test("password mismatch error", () => {
    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("E-MAIL"), {
      target: { value: "test@mail.com" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.change(screen.getByLabelText("CONFIRM PASSWORD"), {
      target: { value: "54321" },
    });

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    expect(
      screen.getByText("Password and Confirm password should be same...")
    ).toBeInTheDocument();
  });

  // ✅ 6. Successful signup
  test("signup success and navigate", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        identity: "123",
        usermail: "test@mail.com",
      }),
    });

    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("E-MAIL"), {
      target: { value: "test@mail.com" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.change(screen.getByLabelText("CONFIRM PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "http://127.0.0.1:3000/auth/signup/",
        expect.any(Object)
      );
    });

    expect(mockedNavigate).toHaveBeenCalledWith(
      "/signup_verify",
      {
        state: {
          id: "123",
          email: "test@mail.com",
          check_box: true,
        },
        replace: true,
      }
    );
  });

  // ✅ 7. API failure
  test("shows error on failed signup", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      statusText: "Bad Request",
      json: async () => ({ detail: "User already exists" }),
    });

    renderComponent();

    fireEvent.change(screen.getByLabelText("USERNAME"), {
      target: { value: "testuser" },
    });

    fireEvent.change(screen.getByLabelText("E-MAIL"), {
      target: { value: "test@mail.com" },
    });

    fireEvent.change(screen.getByLabelText("PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.change(screen.getByLabelText("CONFIRM PASSWORD"), {
      target: { value: "12345" },
    });

    fireEvent.click(screen.getByDisplayValue("SIGN IN"));

    await waitFor(() => {
      expect(
        screen.getByText("Bad Request : User already exists")
      ).toBeInTheDocument();
    });
  });

});