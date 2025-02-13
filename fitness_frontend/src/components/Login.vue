<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">Username:</label>
        <input type="text" v-model="username" id="username" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" v-model="password" id="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
   <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios';
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
          //"http://localhost:8000/auth/token",
          `${apiUrl}/auth/token`,
          formData,
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
        );

        localStorage.setItem("access_token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        eventBus.emit("auth-change");
        this.$router.push("dashboard");
      } catch (err) {
        this.error = err;
      }
}
  }
};
</script>

<style scoped>
.error {
  color: red;
}
</style>
