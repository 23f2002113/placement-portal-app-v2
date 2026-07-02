<template>
  <div class="register">
    <form @submit.prevent="registerUser" @input="clearMessage">
      <h2>Register</h2>

      <label>Name</label>
      <input type="text" v-model="name" placeholder="Name" required>

      <br><br>

      <label>Email</label>
      <input type="email" v-model="email" placeholder="Email" required>

      <br><br>

      <label>Password</label>
      <input type="password" v-model="password" placeholder="Password" required>

      <br><br>

      <label>Role</label>
      <br>
      <select v-model="role" required>
        <option value="" disabled>Select your role</option>
        <option value="student">Student</option>
        <option value="company">Company</option>
      </select>

      <br><br>

      <button type="submit" class="btn-primary">Register</button>
    </form>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from "axios"

export default {
  name: "Register",
  data() {
    return {
      name: "",email: "",password: "",role: "",message: "" 
    }
  },
  methods: {
    clearMessage() {
      this.message = "" 
    },
    async registerUser() {
      this.message = ""
      try {
        await axios.post("http://localhost:5000/auth/register", {
          name: this.name,
          email: this.email,
          password: this.password,
          role: this.role
        })
        
        this.message = this.role === "company" 
          ? "Registration successful! Pending Admin approval." 
          : "Registration successful! Please login."
          
        // Reset inputs
        this.name = ""
        this.email = ""
        this.password = ""
        this.role = ""
      } 
      catch (error) {
        this.message = error.response?.data?.message || "Registration Failed"
      }
    }
  }
}
</script>

<style scoped>

.register{
width:400px;
margin:auto;
margin-top:50px;
}

form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 350px;
}

input{
width:100%;
padding:8px;
}

button{
padding:8px ;
margin-top:10px;
text-align:center
}

.message {
  color: red;
  text-align: center;
  margin-top: 10px;
  font-size: 20px;
}

</style>