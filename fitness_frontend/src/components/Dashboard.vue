<template>
  <div class="dashboard-container">
    <h2>Dashboard</h2>
    <p>Welcome, {{ username }}!</p>
  </div>
</template>

<script>
import { jwtDecode } from "jwt-decode";
import axios from '@/axios';

export default {
  data() {
    return {
      username: '',
    };
  },
  created() {
    this.checkAuthentication();
  },
  methods: {
    checkAuthentication() {
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
  },
};
</script>

<style scoped>
.dashboard-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

h2 {
  color: #2c3e50;
}

p {
  font-size: 18px;
  color: #34495e;
}
</style>
