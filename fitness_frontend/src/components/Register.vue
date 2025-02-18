<template>
  <div class="register-container">
    <h2 class="page-title">Register</h2>
    <form @submit.prevent="register" class="register-form">
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
        <label for="email">Email:</label>
        <input
          type="email"
          v-model="email"
          id="email"
          required
          class="form-input"
          placeholder="Enter your email"
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
        <span class="btn-icon">📝</span> Register
      </button>
    </form>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import axios from "../axios.js";

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async register() {
      try {
        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.post(
          `${apiUrl}/auth/`, {
          username: this.username,
          email: this.email,
          password: this.password
        });
        this.$router.push('/login');
      } catch (err) {
        this.error = 'Registration failed. Please try again.';
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 30px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 20px;
  text-align: center;
}

.register-form {
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
