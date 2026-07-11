<template>
    <div class="register">

        <p v-if="message" class="alert alert-danger position-fixed top-0 start-50 translate-middle-x mt-3 shadow">
            {{ message }}
        </p>

        <form @submit.prevent="registerUser" @input="clearMessage">
            <h2>Register</h2>

            <div>
                <label>Name</label>
                <input type="text" v-model="name" placeholder="Type Your Name " required>
            </div>

            <br>

            <div>
                <label>Email</label>
                <input type="email" v-model="email" placeholder="abcd@gmail.com" required>
            </div>

            <br>

            <div>
                <label>Password</label>
                <input type="password" v-model="password" placeholder="********" required>
            </div>

            <br>

            <div>
                <label>Role</label>

                <select v-model="role" required>
                    <option value="" disabled>Select your role</option>
                    <option value="student">Student</option>
                    <option value="company">Company</option>
                </select>
            </div>

            <br>

            <div class="text-center">
                <button type="submit" class="btn btn-primary">Register</button><br>
                Already have an account? <span><router-link to="/login" class="btn btn-light">Login</router-link></span>
            </div>

        </form>

    </div>
</template>

<script>
import axios from "axios"

export default {
    name: "Register",
    data() {
        return {
            name: "", email: "", password: "", role: "", message: ""
        }
    },
    methods: {
        clearMessage() {
            this.message = ""
        },
        async registerUser() {
            this.message = ""

            // Strong password validation regex pattern
            const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

            if (!passwordPattern.test(this.password)) {
                this.message = "Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a number, and a special character (e.g., @$!%*?&).";
                return;
            }

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
.register {
    width: 400px;
    margin: auto;
    margin-top: 50px;
}

form {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 350px;
}

input {
    width: 100%;
    padding: 8px;
}

button {
    padding: 8px;
    margin-top: 10px;
    text-align: center
}

.btn-primary {
    background: #07325e;
    color: white;
}

.message {
    color: red;
    text-align: center;
    margin-top: 10px;
    font-size: 20px;
}
</style>