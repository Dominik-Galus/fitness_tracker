<template>
  <div class="trainings-container">
    <h2>My Trainings</h2>
    <div v-if="loading">Loading trainings...</div>
    <div v-else>
      <button @click="createTraining" class="create-btn">Create New Training</button>
      <ul class="trainings-list">
        <li v-for="training in trainings" :key="training.training_id" class="training-item">
          <router-link :to="`/trainings/${training.training_id}`" class="training-link">
            {{ training.training_name }} - {{ training.date }}
          </router-link>
        </li>
      </ul>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      trainings: [],
      loading: true,
      error: "",
    };
  },
  created() {
    this.fetchTrainings();
  },
  methods: {
    async fetchTrainings() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        const response = await axios.get(`${apiUrl}/trainings/fetchall/${user_id}`);

        this.trainings = response.data;
        this.loading = false;
      } catch (error) {
        this.error = "Failed to fetch trainings. Please try again.";
        this.loading = false;
      }
    },
    createTraining() {
      this.$router.push("/trainings/create");
    },
  },
};
</script>

<style scoped>
.trainings-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.create-btn {
  padding: 10px;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-bottom: 20px;
  transition: background-color 0.3s ease;
}

.create-btn:hover {
  background-color: #34495e;
}

.trainings-list {
  list-style: none;
  padding: 0;
}

.training-item {
  margin-bottom: 10px;
}

.training-link {
  text-decoration: none;
  color: #2c3e50;
  font-weight: 600;
  padding: 10px;
  display: block;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.training-link:hover {
  background-color: #f5f5f5;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>
