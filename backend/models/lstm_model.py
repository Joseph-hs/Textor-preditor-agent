from collections import Counter
from typing import List, Tuple
import logging

import numpy as np
import tensorflow as tf
from tensorflow import keras

logger = logging.getLogger(__name__)

PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


class LSTMModel:
    """
    Modelo LSTM con ventana de contexto para capturar dependencias reales.
    """

    def __init__(
        self,
        vocab_size: int = 1000,
        embedding_dim: int = 96,
        lstm_units: int = 96,
        sequence_length: int = 5,
    ):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.sequence_length = sequence_length

        self.word_to_idx = {}
        self.idx_to_word = {}
        self.model = None
        self.is_trained = False
        self.pad_index = 0
        self.unk_index = 1

    def train(self, sequences: List[List[str]], epochs: int = 8):
        """
        Entrena el modelo LSTM con ventanas de contexto.
        """
        token_counts = Counter(token for sequence in sequences for token in sequence)
        most_common_tokens = [token for token, _ in token_counts.most_common(self.vocab_size)]
        vocab = [PAD_TOKEN, UNK_TOKEN] + most_common_tokens

        self.word_to_idx = {word: idx for idx, word in enumerate(vocab)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}
        self.pad_index = self.word_to_idx[PAD_TOKEN]
        self.unk_index = self.word_to_idx[UNK_TOKEN]

        X = []
        y = []

        for sequence in sequences:
            encoded = [self.word_to_idx.get(token, self.unk_index) for token in sequence]
            for index in range(1, len(encoded)):
                context = encoded[max(0, index - self.sequence_length):index]
                padded_context = [self.pad_index] * (self.sequence_length - len(context)) + context
                X.append(padded_context)
                y.append(encoded[index])

        if not X:
            logger.warning("No hay suficientes secuencias para entrenar LSTM")
            return

        X = np.array(X, dtype=np.int32)
        y = tf.keras.utils.to_categorical(y, num_classes=len(vocab))

        self.model = keras.Sequential([
            keras.layers.Embedding(
                input_dim=len(vocab),
                output_dim=self.embedding_dim,
                mask_zero=True,
            ),
            keras.layers.LSTM(self.lstm_units),
            keras.layers.Dropout(0.25),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.Dropout(0.15),
            keras.layers.Dense(len(vocab), activation="softmax"),
        ])

        self.model.compile(
            optimizer="adam",
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )

        validation_split = 0.1 if len(X) >= 20 else 0.0
        callbacks = []
        if validation_split > 0:
            callbacks.append(
                keras.callbacks.EarlyStopping(
                    monitor="val_loss",
                    patience=2,
                    restore_best_weights=True,
                )
            )

        fit_kwargs = {
            "x": X,
            "y": y,
            "epochs": epochs,
            "batch_size": 32,
            "verbose": 0,
            "callbacks": callbacks,
        }

        if validation_split > 0:
            fit_kwargs["validation_split"] = validation_split

        self.model.fit(**fit_kwargs)

        self.is_trained = True
        logger.info(
            "LSTM entrenado: %s tokens de vocabulario y %s ejemplos",
            len(vocab),
            len(X),
        )

    def predict_next(self, context: List[str], k: int = 5) -> List[Tuple[str, float]]:
        """
        Predice la siguiente palabra usando una ventana de contexto reciente.
        """
        if not self.is_trained or self.model is None:
            return []

        encoded_context = [
            self.word_to_idx.get(token, self.unk_index)
            for token in context[-self.sequence_length:]
        ]

        if not encoded_context:
            return []

        padded_context = [self.pad_index] * (self.sequence_length - len(encoded_context)) + encoded_context
        input_data = np.array([padded_context], dtype=np.int32)

        predictions = self.model.predict(input_data, verbose=0)[0]
        predictions[self.pad_index] = 0
        predictions[self.unk_index] = 0

        top_k_indices = np.argsort(predictions)[-k:][::-1]
        results = []

        for index in top_k_indices:
            confidence = float(predictions[index])
            word = self.idx_to_word.get(index)
            if not word or confidence <= 0.005:
                continue
            results.append((word, confidence))

        return results
