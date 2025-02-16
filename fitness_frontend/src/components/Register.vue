<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="register" class="register-form">
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" v-model="email" id="email" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit" class="submit-btn register-btn">Register</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from '../axios';
import { useRouter } from "vue-router";

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
        const router = useRouter();
        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.post(
          `${apiUrl}/auth/`, {
          username: this.username,
          email: this.email,
          password: this.password
        });
        router.push('/login');
      } catch (err) {
        this.error = 'Registration failed. Please try again.';
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.register-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  align-items: center;
}

.form-group {
  display: contents;
}

label {
  font-weight: 600;
  text-align: right;
  padding-right: 10px;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 100%;
}

.register-btn {
    grid-column: span 2;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>
