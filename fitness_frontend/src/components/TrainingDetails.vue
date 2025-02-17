<template>
  <div class="training-details-container">
    <h2 class="page-title">Training Details</h2>
    <div v-if="loading" class="loading-message">Loading training details...</div>
    <div v-else>
      <div v-if="trainingDetails" class="training-content">
        <h3 class="training-title">{{ trainingDetails.name }} - {{ formatDate(trainingDetails.date) }}</h3>
        <div v-for="(exercise, exerciseName) in groupedSets" :key="exerciseName" class="exercise-group">
          <h4 class="exercise-name">{{ exerciseName }}</h4>
          <ul class="sets-list">
            <li v-for="(set, index) in exercise" :key="index" class="set-item">
              <div class="set-content">
                <p class="exercise-detail"><strong>Repetitions:</strong> {{ set.repetitions }}</p>
                <p class="exercise-detail"><strong>Weight:</strong> {{ set.weight }} kg</p>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <p v-else class="no-details">No details available for this training.</p>
      <p v-if="error" class="error-message">{{ error }}</p>

      <button @click="goBack" class="go-back-btn">
        <span class="btn-icon">←</span> Go Back
      </button>
    </div>
  </div>
</template>

<script>
import axios from '@/axios';
import { jwtDecode } from "jwt-decode";

export default {
  props: ['id'],
  data() {
    return {
      trainingDetails: null,
      loading: true,
      error: "",
    };
  },
  computed: {
    // Group sets by exercise name
    groupedSets() {
      if (!this.trainingDetails || !this.trainingDetails.sets) return {};

      return this.trainingDetails.sets.reduce((groups, set) => {
        const exerciseName = set.exercise_name;
        if (!groups[exerciseName]) {
          groups[exerciseName] = [];
        }
        groups[exerciseName].push(set);
        return groups;
      }, {});
    },
  },
  created() {
    this.fetchTrainingDetails();
  },
  methods: {
    async fetchTrainingDetails() {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
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
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
    goBack() {
      this.$router.push("/trainings");
    },
  },
};
</script>

<style scoped>
.training-details-container {
  max-width: 800px;
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

.loading-message {
  font-size: 18px;
  color: #666;
  text-align: center;
}

.training-content {
  margin-top: 20px;
}

.training-title {
  font-size: 24px;
  font-weight: 500;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 20px;
}

.exercise-group {
  margin-bottom: 20px;
}

.exercise-name {
  font-size: 20px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 10px;
}

.sets-list {
  list-style: none;
  padding: 0;
}

.set-item {
  margin-bottom: 10px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.set-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.set-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.exercise-detail {
  font-size: 14px;
  color: #555;
}

.no-details {
  text-align: center;
  color: #888;
  font-size: 16px;
}

.error-message {
  font-size: 16px;
  color: #e74c3c;
  text-align: center;
  margin-top: 20px;
}

.go-back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
  transition: background-color 0.3s ease, transform 0.2s ease;
  width: 100%;
}

.go-back-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
}

.go-back-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}
</style>
