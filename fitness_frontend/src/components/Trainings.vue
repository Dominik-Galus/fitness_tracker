<template>
  <div class="trainings-container">
    <h2 class="page-title">My Trainings</h2>
    <div v-if="loading" class="loading-message">Loading trainings...</div>
    <div v-else>
      <button @click="createTraining" class="create-btn">
        <span class="btn-icon">+</span> Create New Training
      </button>

      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by training name..."
          class="search-input"
        />
      </div>

      <div class="sorting-options">
        <label for="sort-by" class="sort-label">Sort By:</label>
        <select id="sort-by" v-model="sortBy" @change="sortTrainings" class="sort-select">
          <option value="name-asc">Name (A-Z)</option>
          <option value="name-desc">Name (Z-A)</option>
          <option value="date-asc">Date (Oldest First)</option>
          <option value="date-desc">Date (Newest First)</option>
        </select>
      </div>

      <ul class="trainings-list">
        <li v-for="training in filteredTrainings" :key="training.training_id" class="training-item">
          <router-link :to="`/trainings/${training.training_id}`" class="training-link">
            <span class="training-name">{{ training.training_name }}</span>
            <span class="training-date">{{ formatDate(training.date) }}</span>
          </router-link>
          <button @click="deleteTraining(training.training_id)" class="delete-btn">
            <span class="btn-icon">🗑️</span> Delete
          </button>
        </li>
      </ul>

      <p v-if="error" class="error-message">{{ error }}</p>
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
      sortedTrainings: [],
      filteredTrainings: [],
      loading: true,
      error: "",
      sortBy: "name-asc",
      searchQuery: "",
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
        this.sortTrainings();
        this.loading = false;
      } catch (error) {
        this.error = "Failed to fetch trainings. Please try again.";
        this.loading = false;
      }
    },
    async deleteTraining(trainingId) {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.delete(`${apiUrl}/trainings/delete/${trainingId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.fetchTrainings();
      } catch (error) {
        this.error = "Failed to delete training. Please try again.";
      }
    },
    createTraining() {
      this.$router.push("/trainings/create");
    },
    sortTrainings() {
      switch (this.sortBy) {
        case "name-asc":
          this.sortedTrainings = [...this.trainings].sort((a, b) =>
            a.training_name.localeCompare(b.training_name)
          );
          break;
        case "name-desc":
          this.sortedTrainings = [...this.trainings].sort((a, b) =>
            b.training_name.localeCompare(a.training_name)
          );
          break;
        case "date-asc":
          this.sortedTrainings = [...this.trainings].sort((a, b) =>
            new Date(a.date) - new Date(b.date)
          );
          break;
        case "date-desc":
          this.sortedTrainings = [...this.trainings].sort((a, b) =>
            new Date(b.date) - new Date(a.date)
          );
          break;
        default:
          this.sortedTrainings = this.trainings;
      }
      this.filterTrainings();
    },
    filterTrainings() {
      if (this.searchQuery) {
        this.filteredTrainings = this.sortedTrainings.filter((training) =>
          training.training_name.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      } else {
        this.filteredTrainings = this.sortedTrainings;
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
  },
  watch: {
    searchQuery() {
      this.filterTrainings();
    },
  },
};
</script>

<style scoped>
.trainings-container {
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

.create-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px 20px;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 20px;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.create-btn:hover {
  background-color: #34495e;
  transform: translateY(-2px);
}

.create-btn .btn-icon {
  margin-right: 8px;
  font-size: 18px;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #f9f9f9;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #3498db;
  outline: none;
}

.sorting-options {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.sort-label {
  font-size: 16px;
  color: #555;
  margin-right: 10px;
}

.sort-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  background-color: #f9f9f9;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.sort-select:hover {
  border-color: #3498db;
}

.trainings-list {
  list-style: none;
  padding: 0;
}

.training-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  margin-bottom: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.training-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
}

.training-link {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: #2c3e50;
  flex-grow: 1;
  border-radius: 12px;
}

.training-name {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 5px;
}

.training-date {
  font-size: 14px;
  color: #777;
}

.delete-btn {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background-color: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.delete-btn:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
}

.delete-btn .btn-icon {
  margin-right: 6px;
}

.error-message {
  font-size: 16px;
  color: #e74c3c;
  text-align: center;
  margin-top: 20px;
}
</style>
