<template>
  <div>
    <h2>Dashboard</h2>
    <p>Welcome, {{ username }}!</p>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      username: ''
    };
  },
  created() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.$router.push('/login');
    } else {
      try {
        const decoded = jwtDecode(token);
        this.username = decoded.sub;
      } catch (error) {
        console.error("Invalid token", error);
        this.$router.push('/login');
      }
    }
  },
};
</script>

<style scoped>
/* Add your styles here */
</style>
