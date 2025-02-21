<template>
  <div class="site-container create-training-container">
    <h2 class="page-title">Create New Training</h2>
    <form @submit.prevent="submitTraining" class="form-group create-training-form">
      <div class="form-group">
        <label for="training_name">Training Name:</label>
        <input
          type="text"
          id="training_name"
          v-model="training.training_name"
          required
          class="form-input"
          placeholder="Enter training name"
        />
      </div>

      <div class="form-group">
        <label for="date">Date:</label>
        <input
          type="date"
          id="date"
          v-model="training.date"
          required
          class="form-input"
        />
      </div>

      <div class="form-group">
        <label for="exercise_search">Search Exercise:</label>
        <input
          type="text"
          id="exercise_search"
          v-model="exerciseSearch"
          @input="filterExercises"
          class="form-input"
          placeholder="Search for an exercise"
        />
        <div v-if="filteredExercises.length > 0" class="exercise-hints">
          <div
            v-for="(exercise, index) in filteredExercises"
            :key="index"
            class="exercise-hint"
            @click="addExercise(exercise.exercise_name)"
          >
            {{ exercise.exercise_name }}
          </div>
        </div>
      </div>

      <div v-for="(exercise, exerciseIndex) in exercises" :key="exerciseIndex" class="exercise-group">
        <div class="exercise-header">
          <h3>Exercise: {{ exercise.exercise_name }}</h3>
          <button
            type="button"
            @click="removeExercise(exerciseIndex)"
            class="submit-btn remove-exercise-btn"
          >
            <span class="btn-icon">🗑️</span> Remove Exercise
          </button>
        </div>

        <div v-for="(set, setIndex) in exercise.sets" :key="setIndex" class="form-group set-group">
          <div class="form-group">
            <label :for="`repetitions_${exerciseIndex}_${setIndex}`">Repetitions:</label>
            <input
              type="number"
              :id="`repetitions_${exerciseIndex}_${setIndex}`"
              v-model="set.repetitions"
              required
              class="form-input"
              placeholder="Enter repetitions"
            />
          </div>

          <div class="form-group">
            <label :for="`weight_${exerciseIndex}_${setIndex}`">Weight (kg):</label>
            <input
              type="number"
              :id="`weight_${exerciseIndex}_${setIndex}`"
              v-model="set.weight"
              required
              class="form-input"
              placeholder="Enter weight"
            />
          </div>

          <button
            type="button"
            @click="removeSet(exerciseIndex, setIndex)"
            class="submit-btn remove-set-btn"
          >
            <span class="btn-icon">🗑️</span> Remove Set
          </button>
        </div>

        <button
          type="button"
          @click="addSet(exerciseIndex)"
          class="submit-btn add-set-btn"
        >
          <span class="btn-icon">➕</span> Add Set
        </button>
      </div>

      <div class="action-buttons">
        <button type="submit" class="submit-btn">
          <span class="btn-icon">💾</span> Create Training
        </button>
        <button type="button" @click="goBack" class="submit-btn go-back-btn">
          <span class="btn-icon">←</span> Go Back
        </button>
      </div>
    </form>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from "../axios.js";
import { jwtDecode } from "jwt-decode";
import { useRouter } from "vue-router";

export default {
  setup() {
    const router = useRouter();
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    const decoded = jwtDecode(token);
    const user_id = decoded.id;

    const training = ref({
      training_name: '',
      date: '',
    });

    const exercises = ref([]);
    const filteredExercises = ref([]);
    const exerciseSearch = ref('');
    const error = ref('');
    let debounceTimeout = null;

    const filterExercises = () => {
      if (debounceTimeout) {
        clearTimeout(debounceTimeout);
      }

      if (exerciseSearch.value === '') {
        filteredExercises.value = [];
        return;
      }

      debounceTimeout = setTimeout(async () => {
        try {
          const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
          const response = await axios.get(`${apiUrl}/exercise/search`, {
            params: {
              characters: exerciseSearch.value,
            },
          });
          filteredExercises.value = response.data || [];
        } catch (err) {
          error.value = "Failed to fetch exercises";
          filteredExercises.value = [];
        }
      }, 1500);
    };

    const addExercise = (exerciseName) => {
      if (exerciseName) {
        exercises.value.push({
          exercise_name: exerciseName,
          sets: [{ repetitions: 0, weight: 0 }],
        });
        exerciseSearch.value = '';
        filteredExercises.value = [];
      }
    };

    const removeExercise = (exerciseIndex) => {
      exercises.value.splice(exerciseIndex, 1);
    };

    const addSet = (exerciseIndex) => {
      exercises.value[exerciseIndex].sets.push({ repetitions: 0, weight: 0 });
    };

    const removeSet = (exerciseIndex, setIndex) => {
      exercises.value[exerciseIndex].sets.splice(setIndex, 1);
    };

    const submitTraining = async () => {
      try {
        const sets = exercises.value.flatMap((exercise) =>
          exercise.sets.map((set) => ({
            exercise_name: exercise.exercise_name,
            repetitions: set.repetitions,
            weight: set.weight,
          }))
        );

        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.post(`${apiUrl}/trainings/?user_id=${user_id}`, {
          training: {
            training_name: training.value.training_name,
            date: training.value.date,
          },
          sets: sets,
        });
        alert("Training created successfully!");
        router.push("/trainings");
      } catch (err) {
        if (err.response.status == 422) {
          alert("Profile data must contain numbers greater than zero");
        } else {
          alert("An error occurred while creating the training.");
        }
      }
    };

    const goBack = () => {
      router.push("/trainings");
    };

    return {
      training,
      exercises,
      filteredExercises,
      exerciseSearch,
      error,
      addExercise,
      removeExercise,
      addSet,
      removeSet,
      submitTraining,
      goBack,
      filterExercises,
    };
  },
};
</script>

<style scoped>
.create-training-container {
  max-width: 800px;
}

.create-training-form {
  gap: 20px;
}

.exercise-hints {
  margin-top: 10px;
}

.exercise-hint {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 5px;
  cursor: pointer;
  background-color: #f9f9f9;
  transition: background-color 0.3s ease;
  color: #2c3e50;
}

.exercise-hint:hover {
  background-color: #3498db;
  color: #fff;
}

.exercise-group {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  background: #f9f9f9;
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.exercise-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.remove-exercise-btn {
  padding: 8px 12px;
  background-color: #e74c3c;
  border-radius: 6px;
  font-size: 14px;
}

.remove-exercise-btn:hover {
  background-color: #c0392b;
}

.set-group {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  background: #ffffff;
  gap: 10px;
}

.remove-set-btn {
  padding: 8px 12px;
  background-color: #e74c3c;
  border-radius: 6px;
  font-size: 14px;
}

.remove-set-btn:hover {
  background-color: #c0392b;
  transform: translateY(-2px);
}

.add-set-btn {
  padding: 10px;
  background-color: #3498db;
  border-radius: 6px;
  font-size: 14px;
}

.add-set-btn:hover {
  background-color: #2980b9;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.go-back-btn {
  flex-grow: 1;
}

</style>
