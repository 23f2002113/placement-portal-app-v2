<template>
    <div class="container py-4">

        <div v-if="alertMessage" class="alert alert-success alert-dismissible fade show mb-4" role="alert">
            <strong>Success:</strong> {{ alertMessage }}
            <button type="button" class="close" @click="alertMessage = ''">
                <span>&times;</span>
            </button>
        </div>

        <!-- 1. ACTIVE SEARCH RESULTS  -->
        <div v-if="searchResults.length > 0 || searchTriggered" class="card p-4 mb-5 border-info shadow-sm bg-white">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h3 class="text-info m-0">Your Search Results</h3>
                <button class="btn btn-sm btn-outline-secondary" @click="clearSearchResults">Clear Results</button>
            </div>

            <div class="table-responsive">
                <table class="table table-bordered table-hover align-middle text-center">
                    <!-- Student Results -->
                    <thead v-if="searchKeyUsed === 'student'" class="table-info">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Name</th>
                            <th>Roll No</th>
                            <th>Department</th>
                        </tr>
                    </thead>
                    <tbody v-if="searchKeyUsed === 'student'">
                        <tr v-for="res in searchResults" :key="res.profile_id">
                            <td>{{ res.profile_id }}</td>
                            <td>{{ res.user_id }}</td>
                            <td class="font-weight-bold">{{ res.name }}</td>
                            <td>{{ res.roll_number }}</td>
                            <td>{{ res.department }}</td>
                        </tr>
                    </tbody>

                    <!-- Company Results  -->
                    <thead v-if="searchKeyUsed === 'company'" class="table-info">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Company Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody v-if="searchKeyUsed === 'company'">
                        <tr v-for="res in searchResults" :key="res.profile_id">
                            <td>{{ res.profile_id }}</td>
                            <td>{{ res.user_id }}</td>
                            <td class="font-weight-bold">{{ res.name }}</td>
                            <td>
                                <span class="badge badge-success">{{ res.status }}</span>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <h4 v-if="searchResults.length === 0" class="text-center text-muted">No results Found!</h4>
            </div>
        </div>

        <!-- 2. STATISTICS  -->
        <div class="row mb-5 justify-content-center">
            <div class="col-md-2 mb-2">
                <div class="card text-center p-3 bg-primary text-white shadow-sm">
                    <h4 class="font-weight-bold">{{ stats.total_companies }}</h4>
                    <small class="text-uppercase">Companies</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card text-center p-3 bg-success text-white shadow-sm">
                    <h4 class="font-weight-bold">{{ stats.total_students }}</h4>
                    <small class="text-uppercase">Students</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card text-center p-3 bg-warning text-dark shadow-sm">
                    <h4 class="font-weight-bold">{{ stats.total_drives }}</h4>
                    <small class="text-uppercase">Drives</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card text-center p-3 bg-info text-white shadow-sm">
                    <h4 class="font-weight-bold">{{ stats.total_applications }}</h4>
                    <small class="text-uppercase">Applications</small>
                </div>
            </div>
            <div class="col-md-2 mb-2">
                <div class="card text-center p-3 bg-dark text-white shadow-sm">
                    <h4 class="font-weight-bold">{{ stats.total_placements }}</h4>
                    <small class="text-uppercase">Placements</small>
                </div>
            </div>
        </div>

        <!--REGISTERED COMPANIES -->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark">Registered Companies</h2>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Name</th>
                            <th>Website</th>
                            <th>Industry</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Action</th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in all_companies" :key="company.profile_id">
                            <td>{{ company.profile_id }}</td>
                            <td>{{ company.user_id }}</td>
                            <td class="font-weight-bold text-primary">{{ company.name }}</td>
                            <td><a :href="company.website" target="_blank">{{ company.website }}</a></td>
                            <td>{{ company.industry }}</td>
                            <td>{{ company.location }}</td>
                            <td>
                                <span class="badge" :class="{
                                        'bg-warning text-dark': company.status === 'pending',
                                        'bg-success': company.status === 'approved',
                                        'bg-danger': company.status === 'rejected'
                                    }">{{ company.status }}</span>
                            </td>
                            <td>
                                <button @click="blacklistCompany(company.profile_id)"
                                    class="btn btn-sm btn-danger">Blacklist</button>
                            </td>
                        </tr>
                        <tr v-if="all_companies.length === 0">
                            <td colspan="8" class="text-center text-muted py-3">No registered companies available.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- REGISTERED STUDENTS -->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark">Registered Students</h2>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Name</th>
                            <th>Roll No</th>
                            <th>CGPA</th>
                            <th>Department</th>
                            <th>Skills</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="student in all_students" :key="student.profile_id">
                            <td>{{ student.profile_id }}</td>
                            <td>{{ student.user_id }}</td>
                            <td class="font-weight-bold text-dark">{{ student.name }}</td>
                            <td>{{ student.roll_number }}</td>
                            <td>{{ student.cgpa }}</td>
                            <td>{{ student.department }}</td>
                            <td>{{ student.skills }}</td>
                            <td>
                                <button @click="blacklistStudent(student.profile_id)"
                                    class="btn btn-sm btn-danger">Blacklist</button>
                            </td>
                        </tr>
                        <tr v-if="all_students.length === 0">
                            <td colspan="8" class="text-center text-muted py-3">No registered students available.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 5. COMPANY APPLICATIONS (PENDING REGISTRATIONS) -->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark"> Pending Companies </h2>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Name</th>
                            <th>Website</th>
                            <th>Industry</th>
                            <th>Location</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="company in pending_companies" :key="company.profile_id">
                            <td>{{ company.profile_id }}</td>
                            <td>{{ company.user_id }}</td>
                            <td class="font-weight-bold">{{ company.name }}</td>
                            <td>
                                <a :href="company.website" target="_blank">{{ company.website }}</a>
                            </td>
                            <td>{{ company.industry }}</td>
                            <td>{{ company.location }}</td>
                            <td>
                                <span class="badge" :class="{
                                        'bg-warning text-dark': company.status === 'pending',
                                        'bg-success': company.status === 'approved',
                                        'bg-danger': company.status === 'rejected'
                                    }">{{ company.status }}</span>
                            </td>
                            <td>
                                <button @click="manageCompany(company.profile_id, 'approve')"
                                    class="btn btn-sm btn-success me-2">Approve</button>
                                <button @click="manageCompany(company.profile_id, 'reject')"
                                    class="btn btn-sm btn-danger me-2">Reject</button>
                            </td>
                        </tr>
                        <tr v-if="pending_companies.length === 0">
                            <td colspan="8" class="text-center text-muted py-3">No pending registration requests.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ONGOING  DRIVES -->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark">Ongoing Drives</h2>
            <div class="table-responsive ">
                <table class="table  table-hover text-center align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Drive Name</th>
                            <th>Drive C_Name</th>
                            <th>Job Title</th>
                            <th>Job Description</th>
                            <th>Min. CGPA </th>
                            <th>Deadline</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="drive in ongoing_drives" :key="drive.id">
                            <td>Drive {{ drive.id }}</td>
                            <td class="font-weight-bold text-dark">{{ drive.company_name }}</td>
                            <td>{{ drive.job_title }}</td>
                            <td>{{ drive.job_description }}</td>
                            <td>{{ drive.eligibility_criteria }}</td>
                            <td>{{ drive.application_deadline }}</td>
                            <td>
                                <button @click="viewDriveDetails(drive)" class="btn btn-sm btn-primary me-2">View Details</button>
                                <button @click="manageDrive(drive.id, 'complete')" class="btn btn-sm btn-success me-2">Mark as complete</button>
                            </td>
                        </tr>
                        <tr v-if="ongoing_drives.length === 0">
                            <td colspan="5" class="text-center text-muted py-3">No ongoing placement drives.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!---PENDING DRIVES--->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark">Pending Drives</h2>
            <div class="table-responsive">
                <table class="table  table-hover text-center align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Drive Name</th>
                            <th>Drive C_Name</th>
                            <th>Job Title</th>
                            <th>Job Description</th>
                            <th>Min. CGPA </th>
                            <th>Deadline</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="drive in pending_drives" :key="drive.id">
                            <td>Drive {{ drive.id }}</td>
                            <td class="font-weight-bold text-dark">{{ drive.company_name }}</td>
                            <td>{{ drive.job_title }}</td>
                            <td>{{ drive.job_description }}</td>
                            <td>{{ drive.eligibility_criteria }}</td>
                            <td>{{ drive.application_deadline }}</td>
                            <td>
                                <button @click="manageDrive(drive.id, 'approve')"
                                    class="btn btn-sm btn-success me-2">Approve</button>
                                <button @click="manageDrive(drive.id, 'reject')"
                                    class="btn btn-sm btn-danger me-2">Reject</button>
                            </td>
                        </tr>
                        <tr v-if="pending_drives.length === 0">
                            <td colspan="7" class="text-center text-muted py-3">No pending placement drives.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!--  STUDENT APPLICATIONS -->
        <div class="card p-4 mb-5 shadow-sm bg-white border-0">
            <h2 class="mb-3 text-dark">Student Applications</h2>
            <div class="table-responsive">
                <table class="table table-hover text-center align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Sr No.</th>
                            <th>Name</th>
                            <th>Drive ID</th>
                            <th>Company Name</th>
                            <th>Date</th>
                            <th>Job Title</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="application in all_applications" :key="application.id">
                            <td>{{ application.id }}</td>
                            <td class="font-weight-bold text-dark">{{ application.student_name }}</td>
                            <td>{{ application.drive_id }}</td>
                            <td>{{ application.company_name }}</td>
                            <td>{{ application.application_date }}</td>
                            <td>{{ application.job_title }}</td>
                            <td>
                                    <span class="badge" :class="{
                                        'bg-primary': application.status === 'applied',
                                        'bg-warning text-dark': application.status === 'shortlisted',
                                        'bg-success': application.status === 'selected',
                                        'bg-danger': application.status === 'rejected'
                                    }">{{ application.status }}</span>
                                </td>
                            <td>
                                <button @click="viewAppDetails(application)" class="btn btn-sm btn-primary">View Details</button>
                            </td>
                        </tr>
                        <tr v-if="all_applications.length === 0">
                            <td colspan="8" class="text-center text-muted py-3">No applications submitted.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!--  VIEW DRIVE DETAILS  -->
        <div v-if="selectedDrive" class="modal-backdrop d-flex align-items-center justify-content-center">
            <div class="card p-4 shadow-lg bg-white" style="max-width: 600px; width: 100%;">
                <div class="border-bottom pb-2 mb-3">
                    <h2 class="m-0 text-primary">Drive {{ selectedDrive.id }}</h2>
                </div>
                <div class="mb-3">
                    <p><strong>Company Name:</strong> {{ selectedDrive.company_name }}</p>
                    <p><strong>Job Title:</strong> {{ selectedDrive.job_title }}</p>
                    <p><strong>Job Description:</strong> {{ selectedDrive.job_description }}</p>
                    <p><strong>Salary:</strong> {{ selectedDrive.salary_package }}</p>
                    <p><strong>Eligibility Criteria:</strong> {{ selectedDrive.eligibility_criteria }}</p>
                    <p><strong>Application Deadline:</strong> {{ selectedDrive.application_deadline }}</p>
                    <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
                </div>
                <div class="text-right">
                    <button @click="selectedDrive = null" class="btn btn-primary">Back</button>
                </div>
            </div>
        </div>

        <!--  VIEW STUDENT APPLICATION DETAILS  -->
        <div v-if="selectedApplication" class="modal-backdrop d-flex align-items-center justify-content-center">
            <div class="card p-4 shadow-lg bg-white" style="max-width: 500px; width: 100%;">
                <div class="border-bottom pb-2 mb-3">
                    <h2 class="m-0 text-primary">Student Application</h2>
                </div>
                <div class="mb-4">
                    <p><strong>Student Name:</strong> {{ selectedApplication.student_name }}</p>
                    <p><strong>Department:</strong> {{ selectedApplication.department }}</p>
                    <p><strong>Drive:</strong> Drive {{ selectedApplication.drive_id }}</p>
                    <p><strong>Job Title:</strong> {{ selectedApplication.job_title }}</p>
                    <p><strong>Job Description:</strong> {{ selectedApplication.job_description }}</p>
                    <p><strong>Status:</strong> <span class="badge" :class="{
                                        'bg-primary': selectedApplication.status === 'applied',
                                        'bg-warning text-dark': selectedApplication.status === 'shortlisted',
                                        'bg-success': selectedApplication.status === 'selected',
                                        'bg-danger': selectedApplication.status === 'rejected'
                                    }">{{ selectedApplication.status }}</span>
                    </p>
                </div>
                <div class="d-flex justify-content-between">
                    <a :href="'http://localhost:5000/static/uploads/resumes/' + selectedApplication.resume_link"
                        class="btn btn-info text-white" target="_blank">View Resume</a>
                    <button @click="selectedApplication = null" class="btn btn-secondary">Back</button>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import axios from "axios"

export default {
    name: "AdminDashboard",
    data() {
        return {
            stats: { total_companies: 0, total_students: 0, total_drives: 0, total_applications: 0, total_placements: 0 },
            all_companies: [],
            all_students: [],
            pending_companies: [],
            ongoing_drives: [],
            pending_drives: [],
            all_applications: [],

            // Search results properties
            searchResults: [],
            searchKeyUsed: "",
            searchTriggered: false,

            // Detail expansion modal properties
            selectedDrive: null,
            selectedApplication: null,

            alertMessage: "",
            headers: {}
        }
    },
    methods: {
        setHeaders() {
            const token = localStorage.getItem("token")
            this.headers = { headers: { "Authentication-Token": token } }
        },
        async fetchDashboardData() {
            this.setHeaders()
            try {
                const statsRes = await axios.get("http://localhost:5000/admin/statistics", this.headers)
                this.stats = statsRes.data

                const compRes = await axios.get("http://localhost:5000/admin/companies", this.headers)
                this.all_companies = compRes.data

                const studentRes = await axios.get("http://localhost:5000/admin/students", this.headers)
                this.all_students = studentRes.data

                const pendingRes = await axios.get("http://localhost:5000/admin/companies/pending", this.headers)
                this.pending_companies = pendingRes.data

                const drivesRes = await axios.get("http://localhost:5000/admin/drives", this.headers)
                this.ongoing_drives = drivesRes.data.ongoing
                this.pending_drives = drivesRes.data.pending

                const appsRes = await axios.get("http://localhost:5000/admin/applications", this.headers)
                this.all_applications = appsRes.data

            }
            catch (err) {
                console.error("Failed to load dashboard statistics and tables.", err)
            }
        },
        async blacklistCompany(id) {
            if (!confirm("Are you sure you want to blacklist this company?")) return
            try {
                const res = await axios.post(`http://localhost:5000/admin/company/${id}/blacklist`, {}, this.headers)
                this.alertMessage = res.data.message
                this.fetchDashboardData()
            }
            catch (err) {
                console.error(err)
            }
        },
        async blacklistStudent(id) {
            if (!confirm("Are you sure you want to blacklist this student?")) return
            try {
                const res = await axios.post(`http://localhost:5000/admin/student/${id}/blacklist`, {}, this.headers)
                this.alertMessage = res.data.message
                this.fetchDashboardData()
            }
            catch (err) {
                console.error(err)
            }
        },
        async manageCompany(id, action) {
            try {
                const res = await axios.put(`http://localhost:5000/admin/company/${id}/${action}`, {}, this.headers)
                this.alertMessage = res.data.message
                this.fetchDashboardData()
            }
            catch (err) {
                console.error(err)
            }
        },
        async manageDrive(id, action) {
            try {
                const res = await axios.put(`http://localhost:5000/admin/drive/${id}/${action}`, {}, this.headers)
                this.alertMessage = res.data.message
                this.fetchDashboardData()
            }
            catch (err) {
                console.error(err)
            }
        },
        viewDriveDetails(drive) {
            this.selectedDrive = drive
        },
        viewAppDetails(application) {
            this.selectedApplication = application
        },

        async handleNavbarSearch() {
            const key = this.$route.query.key
            const query = this.$route.query.q

            if (!key || !query) {
                this.searchResults = []
                this.searchKeyUsed = ""
                this.searchTriggered = false
                return
            }

            this.searchKeyUsed = key
            this.searchTriggered = true

            try {
                if (key === "student") {
                    const res = await axios.get(`http://localhost:5000/admin/students?search=${query}`, this.headers)
                    this.searchResults = res.data
                }
                else if (key === "company") {
                    const res = await axios.get(`http://localhost:5000/admin/companies?search=${query}`, this.headers)
                    this.searchResults = res.data
                }
            }
            catch (err) {
                console.error("Search fetch operation failed.", err)
            }
        },
        clearSearchResults() {
            this.searchResults = []
            this.searchKeyUsed = ""
            this.searchTriggered = false
            this.$router.push("/dashboard/admin")
        }
    },
    created() {
        this.fetchDashboardData()
        this.handleNavbarSearch()
    },
    watch: {
        "$route.query"() {
            this.handleNavbarSearch()
        }
    }
}
</script>

<style scoped>
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

.card {
    border-radius: 8px;
}
</style>