import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the page configuration
st.set_page_config(page_title="Nutrition Calorie Tracker", layout="wide")

# Apply custom header style
st.markdown(
    """
    <div style="background-color:#025246;padding:10px">
    <h2 style="color:white;text-align:center;">Nutrition Calorie Tracker</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Load data with caching
@st.cache_data
def load_data():
    return pd.read_csv("./food1.csv", encoding="mac_roman")

df = load_data()

# Sidebar for user input
st.sidebar.header("Meal Selection")
num_dishes = st.sidebar.number_input("Select number of dishes", min_value=1, max_value=10, value=1)

# Initialize lists to store selections and values
selected_foods, calories_list, protein_list, carbs_list, fat_list, sugar_list, calcium_list = [], [], [], [], [], [], []

# User input for each dish
for i in range(num_dishes):
    st.sidebar.write(f"**Dish {i+1}**")
    food = st.sidebar.selectbox(f"Select Food {i+1}", df["Shrt_Desc"].unique(), key=f"food_{i}")
    servings = st.sidebar.number_input(f"Servings for {food}", min_value=1, max_value=10, value=1, step=1, key=f"serving_{i}")

    # Extract nutrition data
    food_data = df[df["Shrt_Desc"] == food].iloc[0]  # Get the row of selected food
    calories = food_data["Energ_Kcal"] * servings
    protein = food_data["Protein_(g)"] * servings
    carbs = food_data["Carbohydrt_(g)"] * servings
    fat = food_data["Lipid_Tot_(g)"] * servings
    sugar = food_data["Sugar_Tot_(g)"] * servings
    calcium = food_data["Calcium_(mg)"] * servings

    # Store data
    selected_foods.append(food)
    calories_list.append(calories)
    protein_list.append(protein)
    carbs_list.append(carbs)
    fat_list.append(fat)
    sugar_list.append(sugar)
    calcium_list.append(calcium)

# Display summary
st.subheader("Nutritional Breakdown")
total_calories = sum(calories_list)
st.write(f"**Total Calories:** {total_calories} kcal")

# Create a DataFrame for plotting
nutrition_df = pd.DataFrame({
    "Food Item": selected_foods,
    "Calories (kcal)": calories_list,
    "Protein (g)": protein_list,
    "Carbs (g)": carbs_list,
    "Fat (g)": fat_list,
    "Sugar (g)": sugar_list
})

# Display table of selected foods
st.dataframe(nutrition_df)

# Plot a bar chart for nutritional breakdown
fig = px.bar(
    nutrition_df.melt(id_vars=["Food Item"], var_name="Nutrient", value_name="Amount"),
    x="Food Item",
    y="Amount",
    color="Nutrient",
    barmode="group",
    title="Nutrient Breakdown"
)
st.plotly_chart(fig)