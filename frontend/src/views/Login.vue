<template>

<div class="login">

    <form @submit.prevent="loginUser" @input="clearMessage">
        <h2>Login</h2>
        
        <div>
            <label>Email</label>
            <input type="email" v-model="form.email" placeholder="Email" required>
        </div>

        <br>

        <div>
            <label>Password</label>
            <input type="password" v-model="form.password" placeholder="Password" required>
        </div>

        <br>
         
        <div>
            <button type="submit" class="btn btn-primary" >Login</button>
        </div>

    </form>

    <p v-if="message" class="message">{{ message }}</p>

</div>

</template>

<script>

import axios from "axios"

export default {
  name: "Login",
  data() {
    return {
      form: { email: '', password: '' },
      message: "" 
    }
  },
  methods : {
    clearMessage() {
      this.message = "" 
    },
    async loginUser() {
      this.message = ""
      try {
        const response = await axios.post("http://localhost:5000/auth/login", {
          email: this.form.email,       
          password: this.form.password 
        })

        localStorage.setItem("token", response.data.token)
        localStorage.setItem("role", response.data.role)
        localStorage.setItem("name", response.data.name)

        // Route redirection based on verified role
        if (response.data.role === "student") {
          this.$router.push("/dashboard/student")
        } else if (response.data.role === "company") {
          this.$router.push("/dashboard/company")
        } else if (response.data.role === "admin") {
          this.$router.push("/dashboard/admin")
        }
      } 
      catch (error) {
        this.message = error.response?.data?.message || "Invalid Email or Password"
      }
    }
  }
}

</script>

<style scoped>

.login{
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


button {
  padding: 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}


.btn-primary {
  background: #07325e;
  color: white;
}

.message {
  color: red;
  text-align: center;
  margin-top: 15px;
  font-size: 18px;
}
</style>


