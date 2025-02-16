<template>
  <div class="training-details-container">
    <h2>Training Details</h2>
    <div v-if="loading">Loading training details...</div>
    <div v-else>
      <div v-if="trainingDetails">
        <h3>{{ trainingDetails.name }} - {{ trainingDetails.date }}</h3>
        <ul class="sets-list">
          <li v-for="set in trainingDetails.sets" :key="set.exercise_name" class="set-item">
            <p><strong>Exercise:</strong> {{ set.exercise_name }}</p>
            <p><strong>Repetitions:</strong> {{ set.repetitions }}</p>
            <p><strong>Weight:</strong> {{ set.weight }} kg</p>
          </li>
        </ul>
      </div>
      <p v-else class="no-details">No details available for this training.</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import { jwtDecode } from "jwt-decode";
import { useRouter } from "vue-router";

export default {
  props: ['id'],
  data() {
    return {
      trainingDetails: null,
      loading: true,
      error: "",
    };
  },
  created() {
    this.fetchTrainingDetails();
  },
  methods: {
    async fetchTrainingDetails() {
      try {
        const router = useRouter();
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.push("/login");
          return;
        }

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        const response = await axios.get(`${apiUrl}/trainings/fetch/${this.id}`);

        this.trainingDetails = response.data;
        this.loading = false;
      } catch (error) {
        this.error = "Failed to fetch training details. Please try again.";
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.training-details-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.sets-list {
  list-style: none;
  padding: 0;
}

.set-item {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.no-details {
  text-align: center;
  color: #888;
}

.error {
  color: red;
  margin-top: 10px;
  text-align: center;
}
</style>
