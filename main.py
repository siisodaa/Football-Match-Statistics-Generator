# -*- coding: utf-8 -*-
"""main

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qtvdOJSaAQZooQzhS6qkOmmCxW58jgyM
"""

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from tqdm import tqdm
import pickle
import matplotlib.pyplot as plt
from IPython.display import clear_output

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the data from Excel
file_path = 'final.xlsx'  # Update with the correct path to your file
df = pd.read_excel(file_path)

# Ensure all column names are correct
print("Columns in Excel before dropping any columns:", df.columns)
print("First few rows of the dataframe:")
print(df.head())

# Remove text columns
columns_to_drop = ['AWAYTEAM', 'HOMETEAM', 'HTR', 'FTR', 'DATE', 'DIV']  # choose your specific columns that do not contain numerical values
df = df.drop(columns=columns_to_drop, errors='ignore')

# Fill NaN values with 0 (or any other appropriate value)
df = df.fillna(0)

# Convert remaining columns to integers
df = df.astype(int)

# Convert the dataframe to a numpy array
data = df.values

# Normalize the data
data_min = np.min(data, axis=0)
data_max = np.max(data, axis=0)
data = (data - data_min) / (data_max - data_min)

# Define the Generator with more layers and neurons
class Generator(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Generator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.BatchNorm1d(2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Linear(512, output_dim),
        )

    def forward(self, x):
        return self.model(x)

# Define the Discriminator with more layers and neurons
class Discriminator(nn.Module):
    def __init__(self, input_dim):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, 2048),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

# Gradient penalty function
def gradient_penalty(discriminator, real_data, fake_data):
    batch_size = real_data.size(0)
    epsilon = torch.rand(batch_size, 1, device=device)
    epsilon = epsilon.expand_as(real_data)

    interpolated = epsilon * real_data + (1 - epsilon) * fake_data
    interpolated = torch.autograd.Variable(interpolated, requires_grad=True)

    prob_interpolated = discriminator(interpolated)

    gradients = torch.autograd.grad(
        outputs=prob_interpolated,
        inputs=interpolated,
        grad_outputs=torch.ones(prob_interpolated.size(), device=device),
        create_graph=True,
        retain_graph=True
    )[0]

    gradients = gradients.view(batch_size, -1)
    gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()
    return gradient_penalty

# Hyperparameters
input_dim = 100
output_dim = data.shape[1]
lr = 0.00005  # Reduced learning rate
batch_size = 64  # Adjust as needed
epochs = 300000
lambda_gp = 10  # Gradient penalty coefficient

# Initialize the models and move them to GPU
generator = Generator(input_dim, output_dim).to(device)
discriminator = Discriminator(output_dim).to(device)

# Optimizers
optimizer_g = optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
optimizer_d = optim.Adam(discriminator.parameters(), lr=lr, betas=(0.5, 0.999))

# Loss function
criterion = nn.BCELoss()

# Lists to store losses
d_losses = []
g_losses = []

# Training the GAN
for epoch in tqdm(range(epochs)):
    for _ in range(5):  # Train discriminator more frequently
        # Train Discriminator
        real_data = torch.FloatTensor(data[np.random.randint(0, data.shape[0], batch_size)]).to(device)
        noise = torch.FloatTensor(np.random.normal(0, 1, (batch_size, input_dim))).to(device)
        fake_data = generator(noise)

        optimizer_d.zero_grad()
        real_labels = torch.full((batch_size, 1), 0.9, device=device)  # Label smoothing
        fake_labels = torch.zeros(batch_size, 1).to(device)

        real_loss = criterion(discriminator(real_data), real_labels)
        fake_loss = criterion(discriminator(fake_data.detach()), fake_labels)
        gp = gradient_penalty(discriminator, real_data, fake_data)
        d_loss = real_loss + fake_loss + lambda_gp * gp

        d_loss.backward()
        optimizer_d.step()

    # Train Generator
    optimizer_g.zero_grad()
    noise = torch.FloatTensor(np.random.normal(0, 1, (batch_size, input_dim))).to(device)
    fake_data = generator(noise)
    fake_labels = torch.full((batch_size, 1), 0.9, device=device)  # Trick the discriminator with smoothed labels

    g_loss = criterion(discriminator(fake_data), fake_labels)
    g_loss.backward()
    optimizer_g.step()

    # Store losses
    d_losses.append(d_loss.item())
    g_losses.append(g_loss.item())

    # Update live plot every 1000 epochs
    if epoch % 1000 == 0:
        clear_output(wait=True)
        plt.figure(figsize=(10, 5))
        plt.plot(d_losses, label='Discriminator Loss')
        plt.plot(g_losses, label='Generator Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()

    # Print losses every 50,000 epochs
    if epoch % 50000 == 0:
        print(f"Epoch {epoch}: D Loss: {d_loss.item()}, G Loss: {g_loss.item()}")

# Generate new data
noise = torch.FloatTensor(np.random.normal(0, 1, (10, input_dim))).to(device)
generated_data = generator(noise).detach().cpu().numpy()

# De-normalize the data
generated_data = generated_data * (data_max - data_min) + data_min
generated_data = np.round(generated_data)

# Convert generated data to DataFrame and assign column names
generated_df = pd.DataFrame(generated_data, columns=df.columns)

print("Generated Data:")
print(generated_df)

# Save the models
torch.save(generator.state_dict(), 'generator.pth')
torch.save(discriminator.state_dict(), 'discriminator.pth')

# Save the scalers
with open('scalers.pkl', 'wb') as f:
    pickle.dump({'data_min': data_min, 'data_max': data_max}, f)