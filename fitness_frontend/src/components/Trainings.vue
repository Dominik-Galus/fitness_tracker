<template>
  <div class="site-container trainings-container">
    <h2 class="page-title">My Trainings</h2>
    <div v-if="loading" class="loading-spinner">
      <span class="loader"></span>
    </div>
    <div v-else>
      <button @click="createTraining" class="submit-btn create-btn">
        <span class="btn-icon">+</span> Create New Training
      </button>

      <div class="search-container">
        <input
          type="text"
          v-model="searchQuery"
          @input="filterTrainingsDebounced"
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
          <button @click="deleteTraining(training.training_id)" class="submit-btn delete-btn">
            <span class="btn-icon">🗑️</span> Delete
          </button>
        </li>
      </ul>

      <div v-if="isFetchingMore" class="loading-spinner">
        <span class="loader"></span>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <div ref="sentinel" class="sentinel"></div>
    </div>
  </div>
</template>

<script>
import axios from "../axios.js";
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      trainings: [],
      filteredTrainings: [],
      loading: true,
      error: "",
      sortBy: "name-asc",
      searchQuery: "",
      debounceTimeout: null,
      isFetchingMore: false,
      offset: 0,
      hasMore: true,
      observer: null,
    };
  },
  created() {
    this.fetchTrainings(true);
  },
  mounted() {
    this.initScrollObserver();
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect();
    }
  },
  methods: {
    async fetchTrainings(isChange = false) {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const [sortBy, order] = this.sortBy.split("-");

        if (isChange) {
          this.offset = 0;
          this.trainings = [];
          this.hasMore = true;
        }

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        const response = await axios.get(`${apiUrl}/trainings/fetch/sorted/${user_id}`, {
          params: {
            sort_by: sortBy,
            order: order,
            offset: this.offset,
          },
        });

        if (response.data.length > 0) {
          this.trainings = [...this.trainings, ...response.data];
          this.offset += response.data.length;
        } else {
          this.hasMore = false;
        }

        this.filterTrainings();
        this.loading = false;

        this.$nextTick(() => {
          this.initScrollObserver();
        });
      } catch (error) {
        this.error = "Failed to fetch trainings. Please try again.";
        this.loading = false;
      }
    },
    async fetchMoreTrainings() {
      if (this.isFetchingMore || !this.hasMore) return;
      this.isFetchingMore = true;
      await this.fetchTrainings();
      this.isFetchingMore = false;
    },
    initScrollObserver() {
      this.observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && this.hasMore) {
          this.fetchMoreTrainings();
        }
      });

      this.$nextTick(() => {
        if (this.$refs.sentinel) {
          this.observer.observe(this.$refs.sentinel);
        }
      });
    },
    async deleteTraining(trainingId) {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          this.$router.push("/login");
          return;
        }
        const decoded = jwtDecode(token);
        const user_id = decoded.id;

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.delete(`${apiUrl}/trainings/delete/${trainingId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          params: {
              user_id: user_id,
          },
        });

        this.fetchTrainings(true);
      } catch (error) {
        this.error = "Failed to delete training. Please try again.";
      }
    },
    createTraining() {
      this.$router.push("/trainings/create");
    },
    sortTrainings() {
      this.fetchTrainings(true);
    },
    filterTrainings() {
      if (this.debounceTimeout) {
        clearTimeout(this.debounceTimeout);
      }

      const token = localStorage.getItem("access_token");
      if (!token) {
        this.$router.push("/login");
        return;
      }

      const decoded = jwtDecode(token);
      const user_id = decoded.id;


      if (this.searchQuery === "") {
        this.filteredTrainings = this.trainings;
        return;
      }

      this.debounceTimeout = setTimeout(async () => {
        try {
          const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
          const response = await axios.get(`${apiUrl}/trainings/fetch/search`, {
            params: {
              characters: this.searchQuery,
              user_id: user_id,
            },
          });
          this.filteredTrainings = response.data || [];
        } catch (error) {
          this.error = "Failed to fetch trainings. Please try again.";
          this.filteredTrainings = [];
        }
      }, 1500);
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
}

.create-btn {
  width: 100%;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.create-btn:hover {
  background-color: #34495e;
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
  padding: 8px 12px;
  background-color: #e74c3c;
  border-radius: 6px;
  font-size: 14px;
}

.delete-btn:hover {
  background-color: #c0392b;
}

.delete-btn .btn-icon {
  margin-right: 6px;
}

.sentinel {
  height: 50px;
}
</style>
