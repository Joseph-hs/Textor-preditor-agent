const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  async predict(text, userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          user_id: userId,
          max_suggestions: 5
        })
      });

      if (!response.ok) throw new Error('Error en predicción');
      return await response.json();
    } catch (error) {
      console.error('Error en API predict:', error);
      throw error;
    }
  },

  async sendFeedback(text, selected, userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          selected: selected,
          user_id: userId
        })
      });

      if (!response.ok) throw new Error('Error en feedback');
      return await response.json();
    } catch (error) {
      console.error('Error en API feedback:', error);
    }
  },

  async getUserStats(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/user-stats/${userId}`);
      if (!response.ok) throw new Error('Error obteniendo estadísticas');
      return await response.json();
    } catch (error) {
      console.error('Error en API getUserStats:', error);
      return {
        user_id: userId,
        words_learned: 0,
        total_predictions: 0,
        accuracy: 0
      };
    }
  }
};