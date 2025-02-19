<template>
  <div class="login-container">
    <h2 class="page-title">Login</h2>
    <form @submit.prevent="login" class="login-form">
      <div class="form-group">
        <label for="username">Username:</label>
        <input
          type="text"
          v-model="username"
          id="username"
          required
          class="form-input"
          placeholder="Enter your username"
        />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input
          type="password"
          v-model="password"
          id="password"
          required
          class="form-input"
          placeholder="Enter your password"
        />
      </div>
      <button type="submit" class="submit-btn">
        <span class="btn-icon">🔑</span> Login
      </button>
    </form>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import axios from "../axios.js";
import eventBus from "../eventBus";

export default {
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async login() {
      try {
        const formData = new URLSearchParams();
        formData.append("username", this.username);
        formData.append("password", this.password);

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        const response = await axios.post(
          `${apiUrl}/auth/token`,
          formData,
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
        );

        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        eventBus.emit("auth-change");
        this.$router.push("/");
      } catch (err) {
        this.error = err.response ? err.response.data.detail : err.message;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.submit-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

.error-message {
  font-size: 16px;
  color: #e74c3c;
  text-align: center;
  margin-top: 20px;
}
</style>
