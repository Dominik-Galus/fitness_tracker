<template>
  <div>
    <h1>Create New Training</h1>
    <form @submit.prevent="submitTraining">
      <label for="training_name">Training Name:</label>
      <input type="text" id="training_name" v-model="training.training_name" required />

      <label for="date">Date:</label>
      <input type="date" id="date" v-model="training.date" required />

      <div v-for="(set, index) in training.sets" :key="index">
        <label :for="`exercise_name_${index}`">Exercise Name:</label>
        <input type="text" :id="`exercise_name_${index}`" v-model="set.exercise_name" required />

        <label :for="`repetitions_${index}`">Repetitions:</label>
        <input type="number" :id="`repetitions_${index}`" v-model="set.repetitions" required />

        <label :for="`weight_${index}`">Weight (kg):</label>
        <input type="number" :id="`weight_${index}`" v-model="set.weight" required />

        <button type="button" @click="removeSet(index)">Remove Set</button>
      </div>

      <button type="button" @click="addSet">Add Set</button>
      <button type="submit">Create Training</button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  setup() {
    const training = ref({
      training_name: '',
      date: '',
      sets: [{ exercise_name: '', repetitions: 0, weight: 0 }],
    });

    const addSet = () => {
      training.value.sets.push({ exercise_name: '', repetitions: 0, weight: 0 });
    };

    const removeSet = (index) => {
      training.value.sets.splice(index, 1);
    };

    const submitTraining = async () => {
      const userId = localStorage.getItem('user_id');
      try {
        await axios.post('http://localhost:8000/trainings/', {
          user_id: userId,
          training: {
            training_name: training.value.training_name,
            date: training.value.date,
          },
          sets: training.value.sets,
        });
        alert('Training created successfully!');
      } catch (error) {
        alert('Error creating training.');
      }
    };

    return {
      training,
      addSet,
      removeSet,
      submitTraining,
    };
  },
};
</script>
