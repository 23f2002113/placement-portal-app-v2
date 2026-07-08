<template>
    <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h2 text-dark font-weight-bold">Student Dashboard</h1>
            <button @click="loadStudentDashboard" class="btn btn-sm btn-outline-primary">Refresh Dashboard</button>
        </div>

        <!-- Alert messages -->
        <div v-if="alertMessage" class="alert alert-success alert-dismissible fade show mb-4 text-center" role="alert">
            {{ alertMessage }}
            <button type="button" class="close" @click="alertMessage = ''">
                <span>&times;</span>
            </button>
        </div>

        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show mb-4 text-center" role="alert">
            {{ errorMessage }}
            <button type="button" class="close" @click="errorMessage = ''">
                <span>&times;</span>
            </button>
        </div>

        <div class="row">

            <!-- SECTION: Edit and View Student Profile Details  & Upload Resume -->
            <div class="col-md-4 mb-4">
                <div class="card p-4 shadow-sm bg-white border-0 mb-4">
                    <h3 class="mb-3 text-dark">My Profile</h3>
                    <form @submit.prevent="updateStudentProfile">

                        <div class="mb-3">
                            <label class="font-weight-bold">Full Name</label>
                            <input type="text" class="form-control" :value="form.name" disabled>
                        </div>

                        <div class="mb-3">
                            <label class="font-weight-bold">Email Address</label>
                            <input type="email" class="form-control" :value="form.email" disabled>
                        </div>

                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="font-weight-bold">Roll Number</label>
                                <input type="text" class="form-control" v-model="form.roll_no" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="font-weight-bold">CGPA</label>
                                <input type="number" step="0.01" min="0" max="10" class="form-control"
                                    v-model="form.cgpa" required>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="font-weight-bold">Education Qualification</label>
                            <input type="text" class="form-control" v-model="form.education" placeholder="e.g. B.Tech ">
                        </div>

                        <div class="mb-3">
                            <label class="font-weight-bold">Department</label>
                            <input type="text" class="form-control" v-model="form.department"
                                placeholder="e.g. Mechanical Engineering">
                        </div>

                        <div class="mb-3">
                            <label class="font-weight-bold">Skills</label>
                            <textarea class="form-control" rows="2" v-model="form.skills"
                                placeholder="e.g. Python, SQL, ML, Git"></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary btn-block">Update Profile </button>
                    </form>
                </div>

                <!-- Section: Resume Uploader -->
                <div class="card p-4 shadow-sm bg-white border-0">
                    <h3 class="mb-3 text-dark">My Resume</h3>
                    <div v-if="form.resume_link" class="alert alert-light border text-center mb-3">
                        <a :href="'http://localhost:5000/static/uploads/resumes/' + form.resume_link" target="_blank"
                            class="font-weight-bold text-success text-decoration-none">
                            📄 View Current Resume PDF
                        </a>
                    </div>

                    <div v-else class="alert alert-warning text-center small mb-3">
                        You must upload a PDF resume before applying to drives.
                    </div>

                    <form @submit.prevent="uploadResumeFile">
                        <div class="custom-file mb-3">
                            <input type="file" ref="fileInput" class="custom-file-input" @change="onFileSelected"
                                accept=".pdf" required>
                            <label class="custom-file-label">{{ selectedFileName || 'Choose PDF File...' }}</label>
                        </div>
                        <button type="submit" class="btn btn-outline-success btn-block" :disabled="!selectedFile">
                            Upload Resume File
                        </button>
                    </form>
                </div>
            </div>

            <div class="col-md-8">

                <!-- Open Drives Searching  -->
                <div class="card p-4 mb-4 shadow-sm bg-white border-0">
                    <div class="d-flex mb-3 gap-2">
                        <input type="text" class="form-control"
                            placeholder="Search jobs by company name, title or skills" v-model="searchQuery"
                            @keyup.enter="fetchAvailableDrives">
                        <button class="btn btn-primary px-4" @click="fetchAvailableDrives">Search</button>
                        <button v-if="searchQuery" class="btn btn-outline-secondary"
                            @click="clearSearchQuery">Clear</button>
                    </div>

                    <h3 class="mb-3 text-dark">Available Placement Drives</h3>
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover align-middle">
                            <thead class="table-dark">
                                <tr>
                                    <th>Company</th>
                                    <th>Job Title</th>
                                    <th>Salary Package</th>
                                    <th>Min CGPA Cutoff</th>
                                    <th>Deadline</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="drive in drives" :key="drive.id">
                                    <td class="font-weight-bold text-primary">{{ drive.company_name }}</td>
                                    <td>{{ drive.job_title }}</td>
                                    <td>{{ drive.salary_package }}</td>
                                    <td>CGPA >= {{ drive.min_cgpa_criteria }}</td>
                                    <td>{{ drive.application_deadline }}</td>
                                    <td>
                                        <button @click="viewDriveDetails(drive)"
                                            class="btn btn-sm btn-primary me-1">View</button>
                                        <button v-if="drive.already_applied" class="btn btn-sm btn-secondary"
                                            disabled>Applied</button>
                                        <button v-else-if="Number(form.cgpa) < Number(drive.min_cgpa_criteria)"
                                            class="btn btn-sm btn-danger" disabled title="CGPA Cutoff mismatch">
                                            Ineligible
                                        </button>
                                        <button v-else @click="applyForJob(drive.id)"
                                            class="btn btn-sm btn-success">Apply</button>
                                    </td>
                                </tr>

                                <tr v-if="drives.length === 0">
                                    <td colspan="6" class="text-center text-muted py-3">No matching active placement
                                        drives found.</td>
                                </tr>

                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- View Drive Details-->
                <div v-if="selectedDrive" class="modal-backdrop d-flex align-items-center justify-content-center">
                    <div class="card p-4 shadow-lg bg-white" style="max-width: 600px; width: 100%;">
                        <div class="border-bottom pb-2 mb-3">
                            <h2 class="m-0 text-primary">{{ selectedDrive.company_name }} - Drive Details</h2>
                        </div>
                        <div class="mb-3 text-left">
                            <p><strong>Job Title:</strong> {{ selectedDrive.job_title }}</p>
                            <p><strong>Job Description:</strong> {{ selectedDrive.job_description }}</p>
                            <p><strong>Salary Package:</strong> {{ selectedDrive.salary_package }}</p>
                            <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
                            <p><strong>CGPA Cutoff:</strong> CGPA >= {{ selectedDrive.min_cgpa_criteria }}</p>
                            <p><strong>Deadline:</strong> {{ selectedDrive.application_deadline }}</p>
                        </div>
                        <div class="text-right">
                            <button @click="selectedDrive = null" class="btn btn-secondary">Close</button>
                        </div>
                    </div>
                </div>

                <!-- Application History  -->
                <div class="card p-4 shadow-sm bg-white border-0">
                    <h3 class="mb-3 text-dark">Student Application History </h3>
                    <div class="table-responsive">
                        <table class="table table-bordered table-hover align-middle text-center">
                            <thead class="table-dark">
                                <tr>
                                    <th>App ID</th>
                                    <th>Company</th>
                                    <th>Job Position</th>
                                    <th>Package Details</th>
                                    <th>Submitted Date</th>
                                    <th>Selection Status</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr v-for="application in applications" :key="application.id">
                                    <td>{{ application.id }}</td>
                                    <td class="font-weight-bold text-dark">{{ application.company_name }}</td>
                                    <td>{{ application.job_title }}</td>
                                    <td>{{ application.salary_package }}</td>
                                    <td>{{ application.application_date }}</td>
                                    <td>
                                        <span class="badge" :class="{
                                            'bg-primary': application.status === 'applied',
                                            'bg-warning text-dark': application.status === 'shortlisted',
                                            'bg-success': application.status === 'selected',
                                            'bg-danger': application.status === 'rejected'
                                        }">{{ application.status }}</span>
                                    </td>
                                </tr>

                                <tr v-if="applications.length === 0">
                                    <td colspan="6" class="text-center text-muted py-3">You have not submitted any
                                        placement applications yet.</td>
                                </tr>

                            </tbody>
                        </table>
                    </div>
                </div>

            </div>

        </div>
    </div>
</template>


<script>
import axios from "axios"

export default {
    name: "StudentDashboard",
    data() {
        return {
            form: { name: "", email: "", roll_no: "", cgpa: 0.0, education: "", department: "", skills: "", resume_link: "" },
            drives: [],
            applications: [],
            searchQuery: "",

            // Resume file upload trackers
            selectedFile: null,
            selectedDrive: null,
            selectedFileName: "",

            alertMessage: "",
            errorMessage: "",
            headers: {}
        }
    },
    methods: {
        setHeaders() {
            const token = localStorage.getItem("token")
            this.headers = { headers: { "Authentication-Token": token } }
        },

        async loadStudentDashboard() {
            this.setHeaders()
            this.alertMessage = ""
            this.errorMessage = ""
            try {
                const profileRes = await axios.get("http://localhost:5000/student/profile", this.headers)
                this.form = profileRes.data

                this.fetchAvailableDrives()

                const appsRes = await axios.get("http://localhost:5000/student/applications", this.headers)
                this.applications = appsRes.data

            }
            catch (err) {
                console.error("Failed to load student dashboard.", err)
            }
        },

        async updateStudentProfile() {
            this.alertMessage = ""
            this.errorMessage = ""
            try {
                await axios.put("http://localhost:5000/student/profile", this.form, this.headers)
                this.alertMessage = "Your profile information was updated successfully."
                this.loadStudentDashboard()
            }
            catch (err) {
                this.errorMessage = err.response?.data?.message || "Failed to update profile details."
            }
        },

        onFileSelected(event) {
            const file = event.target.files[0]
            if (file) {
                this.selectedFile = file
                this.selectedFileName = file.name
            }
        },

        async uploadResumeFile() {
            if (!this.selectedFile) return
            this.alertMessage = ""
            this.errorMessage = ""

            const formData = new FormData()
            formData.append("resume", this.selectedFile)

            try {
                const res = await axios.post("http://localhost:5000/student/upload-resume", formData, {
                    headers: {
                        "Authentication-Token": localStorage.getItem("token"),
                        "Content-Type": "multipart/form-data"
                    }
                })
                this.alertMessage = res.data.message
                this.selectedFile = null
                this.selectedFileName = ""
                this.loadStudentDashboard()
            }
            catch (err) {
                this.errorMessage = err.response?.data?.message || "Failed to upload resume file."
            }
        },

        async fetchAvailableDrives() {
            try {
                const drivesRes = await axios.get(`http://localhost:5000/student/drives?search=${this.searchQuery}`, this.headers)
                this.drives = drivesRes.data
            }
            catch (err) {
                console.error(err)
            }
        },
        clearSearchQuery() {
            this.searchQuery = ""
            this.fetchAvailableDrives()
        },

        async applyForJob(driveId) {
            this.alertMessage = ""
            this.errorMessage = ""
            try {
                const res = await axios.post(`http://localhost:5000/student/apply/${driveId}`, {}, this.headers)
                this.alertMessage = res.data.message
                this.loadStudentDashboard()
            }
            catch (err) {
                this.errorMessage = err.response?.data?.message || "Failed to submit application."
            }
        },
        viewDriveDetails(drive) {
            this.selectedDrive = drive
        }
    },
    created() {
        this.loadStudentDashboard()
    }
}
</script>

<style scoped>
.card {
    border-radius: 8px;
    overflow: hidden;
}

.custom-file-input {
    cursor: pointer;
}

.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(2px);
    z-index: 1050;
}
</style>