# GAN for Synthetic Data Generation

This project demonstrates how to use a Generative Adversarial Network (GAN) to generate synthetic data based on an Excel dataset. The GAN consists of a Generator and a Discriminator with more layers and neurons for better performance.

### Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Code Overview](#code-overview)
- [Model Saving and Evaluation](#model-saving-and-evaluation)
- [Results](#results)
- [Contributing](#contributing)

### Installation

#### Prerequisites

- Python 3.8+
- PyTorch
- pandas
- numpy
- tqdm
- matplotlib
- pickle

#### Installation Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/gan-synthetic-data.git
    cd gan-synthetic-data
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    ```

2. Run the script:
    ```bash
    python main.py
    ```

    This will load the dataset, preprocess the data, train the GAN, and generate synthetic data.

### Code Overview

The main script performs the following steps:

1. **Load the Data**: Loads the data from the specified Excel file.
2. **Preprocess the Data**: Drops non-numeric columns, fills NaN values, and converts data to integers.
3. **Normalize the Data**: Normalizes the data for training the GAN.
4. **Define the Generator and Discriminator**: Sets up the GAN with more layers and neurons.
5. **Gradient Penalty Function**: Implements the gradient penalty for the GAN.
6. **Training the GAN**: Trains the GAN using the specified hyperparameters.
7. **Generate New Data**: Generates synthetic data using the trained Generator.
8. **Save the Models**: Saves the trained Generator and Discriminator models.
9. **Save the Scalers**: Saves the data scalers for future use.

### Model Saving and Evaluation

The Generator and Discriminator models are saved during training. The losses for both models are plotted and displayed during training.

### Results

After running the script, the generated synthetic data will be displayed and saved. The models and scalers will also be saved for future use.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
