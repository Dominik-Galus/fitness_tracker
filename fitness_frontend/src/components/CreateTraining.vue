<template>
  <div class="create-training-container">
    <h2>Create New Training</h2>
    <form @submit.prevent="submitTraining" class="create-training-form">
      <div class="form-group">
        <label for="training_name">Training Name:</label>
        <input
          type="text"
          id="training_name"
          v-model="training.training_name"
          required
        />
      </div>

      <div class="form-group">
        <label for="date">Date:</label>
        <input
          type="date"
          id="date"
          v-model="training.date"
          required
        />
      </div>

      <div v-for="(set, index) in training.sets" :key="index" class="set-group">
        <div class="form-group">
          <label :for="`exercise_name_${index}`">Exercise Name:</label>
          <input
            type="text"
            :id="`exercise_name_${index}`"
            v-model="set.exercise_name"
            required
          />
        </div>

        <div class="form-group">
          <label :for="`repetitions_${index}`">Repetitions:</label>
          <input
            type="number"
            :id="`repetitions_${index}`"
            v-model="set.repetitions"
            required
          />
        </div>

        <div class="form-group">
          <label :for="`weight_${index}`">Weight (kg):</label>
          <input
            type="number"
            :id="`weight_${index}`"
            v-model="set.weight"
            required
          />
        </div>

        <button
          type="button"
          @click="removeSet(index)"
          class="remove-set-btn"
        >
          Remove Set
        </button>
      </div>

      <button type="button" @click="addSet" class="add-set-btn">
        Add Set
      </button>

      <button type="submit" class="submit-btn">Create Training</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
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
      sets: [{ exercise_name: '', repetitions: 0, weight: 0 }],
    });

    const error = ref('');

    const addSet = () => {
      training.value.sets.push({ exercise_name: '', repetitions: 0, weight: 0 });
    };

    const removeSet = (index) => {
      training.value.sets.splice(index, 1);
    };

    const submitTraining = async () => {
      try {
        const apiUrl = import.meta.env.VITE_BACKEND_API_URL;
        await axios.post(`${apiUrl}/trainings/?user_id=${user_id}`, {
          training: {
            training_name: training.value.training_name,
            date: training.value.date,
          },
          sets: training.value.sets,
        });
        alert('Training created successfully!');
        router.push("/trainings");
      } catch (err) {
          alert('An error occurred while creating the training.');
      }
    };

    return {
      training,
      error,
      addSet,
      removeSet,
      submitTraining,
    };
  },
};
</script>

<style scoped>
.create-training-container {
  max-width: 600px;
  margin: 50px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.create-training-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

label {
  font-weight: 600;
  color: #2c3e50;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  width: 100%;
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #2c3e50;
  outline: none;
}

.set-group {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  background: #f9f9f9;
}

.remove-set-btn {
  padding: 8px 12px;
  background-color: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
  align-self: flex-start;
}

.remove-set-btn:hover {
  background-color: #c0392b;
}

.add-set-btn {
  padding: 10px;
  background-color: #3498db;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.add-set-btn:hover {
  background-color: #2980b9;
}

.submit-btn {
  padding: 10px;
  background-color: #2c3e50;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s ease;
}

.submit-btn:hover {
  background-color: #34495e;
}

.error {
  color: #e74c3c;
  margin-top: 10px;
  text-align: center;
}
</style>
