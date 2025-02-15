<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="login" class="login-form">
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit" class="submit-btn">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from '../axios';
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
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

label {
  font-weight: 600;
  margin-bottom: 5px;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
