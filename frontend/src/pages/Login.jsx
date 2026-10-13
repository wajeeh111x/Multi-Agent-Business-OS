import { useState } from "react";
import { motion } from "framer-motion";
import {
  Sparkles,
  Mail,
  Lock,
  User,
} from "lucide-react";

import {
  loginUser,
  registerUser,
} from "../api";

function Login({ onLogin }) {

  const [isRegistering, setIsRegistering] =
    useState(false);

  const [username, setUsername] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");

  async function handleSubmit(e) {

    e.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {

      // -----------------------------
      // REGISTER
      // -----------------------------

      if (isRegistering) {

        await registerUser(
          username,
          email,
          password
        );

        setSuccess(
          "Account created successfully. You can now sign in."
        );

        setIsRegistering(false);

        setUsername("");
        setPassword("");

      }

      // -----------------------------
      // LOGIN
      // -----------------------------

      else {

        const data = await loginUser(
          email,
          password
        );

        console.log("LOGIN RESPONSE:", data);

        if (!data.access_token) {
          throw new Error("No access token received from backend.");
        }

        localStorage.setItem(
          "access_token",
          data.access_token
        );

        console.log(
          "TOKEN AFTER SAVE:",
          localStorage.getItem("access_token")
        );

        onLogin();

      }

    } catch (err) {

      setError(
        err.message ||
        (
          isRegistering
            ? "Registration failed"
            : "Invalid email or password"
        )
      );

    } finally {

      setLoading(false);

    }
  }

  function switchMode() {

    setIsRegistering(!isRegistering);

    setError("");
    setSuccess("");

    setUsername("");
    setEmail("");
    setPassword("");
  }

  return (

    <div className="login-screen">

      <motion.div
        className="login-card"

        initial={{
          opacity: 0,
          y: 20,
        }}

        animate={{
          opacity: 1,
          y: 0,
        }}

        transition={{
          duration: 0.4,
        }}
      >

        {/* LOGO */}

        <div className="login-logo">

          <Sparkles size={25} />

        </div>

        {/* TITLE */}

        <h1>

          {isRegistering
            ? "Create your account"
            : "Welcome back"}

        </h1>

        <p>

          {isRegistering
            ? "Create your AI Business OS account"
            : "Sign in to your AI Business OS"}

        </p>

        {/* ERROR */}

        {error && (

          <div className="login-error">

            {error}

          </div>

        )}

        {/* SUCCESS */}

        {success && (

          <div className="login-success">

            {success}

          </div>

        )}

        {/* FORM */}

        <form onSubmit={handleSubmit}>

          {/* USERNAME */}

          {isRegistering && (

            <>
              <label>
                Username
              </label>

              <div className="login-input">

                <User size={17} />

                <input
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) =>
                    setUsername(e.target.value)
                  }
                  required
                />

              </div>
            </>

          )}

          {/* EMAIL */}

          <label>
            Email
          </label>

          <div className="login-input">

            <Mail size={17} />

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />

          </div>

          {/* PASSWORD */}

          <label>
            Password
          </label>

          <div className="login-input">

            <Lock size={17} />

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
            />

          </div>

          {/* SUBMIT */}

          <button
            type="submit"
            className="primary-button login-button"
            disabled={loading}
          >

            {loading
              ? (
                isRegistering
                  ? "Creating account..."
                  : "Signing in..."
              )
              : (
                isRegistering
                  ? "Create account"
                  : "Sign in"
              )}

          </button>

        </form>

        {/* SWITCH */}

        <div className="login-switch">

          <span>

            {isRegistering
              ? "Already have an account?"
              : "Don't have an account?"}

          </span>

          <button
            type="button"
            onClick={switchMode}
          >

            {isRegistering
              ? "Sign in"
              : "Create account"}

          </button>

        </div>

      </motion.div>

    </div>
  );
}

export default Login;