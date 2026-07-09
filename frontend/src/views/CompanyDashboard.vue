<template>
    <div class="container py-4">

        <!-- 1. Pending approval Dashboard -->
        <div v-if="profileStatus === 'pending'"
            class="text-center py-5 bg-white rounded shadow-sm border border-warning">
            <h2 class="text-warning font-weight-bold mb-3">Verification Pending</h2>
            <p class="lead text-muted px-4">
                Your corporate profile has been registered successfully. You will gain access to job creation and
                applicant lists as soon as the Institute Placement Cell approves your profile.
            </p>
        </div>

        <!-- 2. Approved Dashboard -->
        <div v-else>
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h2 text-dark font-weight-bold">Recruiter Workspace</h1>
                <button @click="fetchDashboardData" class="btn btn-sm btn-outline-primary">Refresh Data</button>
            </div>

            <!-- Statistics -->
            <div class="row mb-5 justify-content-center">
                <div class="col-md-3">
                    <div class="card text-center p-3 bg-primary text-white shadow-sm border-0">
                        <h4 class="font-weight-bold">{{ stats.total_drives }}</h4>
                        <small class="text-uppercase">Total Drives Created</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center p-3 bg-success text-white shadow-sm border-0">
                        <h4 class="font-weight-bold">{{ stats.total_applications }}</h4>
                        <small class="text-uppercase">Total Applications Received</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-center p-3 bg-secondary text-white shadow-sm border-0">
                        <h4 class="font-weight-bold">{{ stats.total_shortlisted }}</h4>
                        <small class="text-uppercase">Total Shortlisted Candidates</small>
                    </div>
                </div>
            </div>

            <!-- Alert Message -->
            <div v-if="alertMessage" class="alert alert-success alert-dismissible fade show mb-4" role="alert">
                <strong>Success:</strong> {{ alertMessage }}
                <button type="button" class="close" @click="alertMessage = ''">
                    <span>&times;</span>
                </button>
            </div>

            <div class="row mb-5">
                <!-- Section: Post a New Drive on left -->
                <div class="col-md-8">
                    <div class="card p-4 shadow-sm bg-white border-0">
                        <h3 class="mb-3 text-dark">Post New Placement Drive</h3>
                        <form @submit.prevent="createPlacementDrive">

                            <div class="form-group mb-3">
                                <label class="font-weight-bold">Job Title</label>
                                <input type="text" class="form-control" v-model="jobForm.job_title" required
                                    placeholder="e.g. ML Engineer">
                            </div>

                            <div class="form-group mb-3">
                                <label class="font-weight-bold">Job Description</label>
                                <textarea class="form-control" rows="3" v-model="jobForm.job_description" required
                                    placeholder="Details about roles, required skills, and experience..."></textarea>
                            </div>

                            <div class="row">
                                <div class="col-md-6 form-group mb-3">
                                    <label class="font-weight-bold">Salary (CTC Package)</label>
                                    <input type="text" class="form-control" v-model="jobForm.salary_package"
                                        placeholder="e.g. 12 LPA" required>
                                </div>
                                <div class="col-md-6 form-group mb-3">
                                    <label class="font-weight-bold">Minimum CGPA Criteria</label>
                                    <input type="number" step="0.01" min="0" max="10" class="form-control"
                                        v-model="jobForm.min_cgpa_criteria" required>
                                </div>
                            </div>

                            <div class="form-group mb-3">
                                <label class="font-weight-bold">Application Deadline</label>
                                <input type="date" class="form-control" v-model="jobForm.application_deadline" required>
                            </div>
                            <div class="text-end">
                                <button type="submit" class="btn btn-success px-4">Post Drive</button>
                            </div>

                        </form>
                    </div>
                </div>

                <!-- Section: Company Profile View/Edit on right -->
                <div class="col-md-4">
                    <div class="card p-4 shadow-sm bg-white border-0">
                        <h3 class="mb-3 text-dark">Recruiter Profile</h3>
                        <form @submit.prevent="updateProfile">
                            <div class="mb-3">
                                <label class="font-weight-bold">Company Name</label>
                                <input type="text" class="form-control" :value="profile.name" disabled>
                                <small class="text-muted">Contact admin to alter name</small>
                            </div>

                            <div class="mb-3">
                                <label class="font-weight-bold">Industry Type</label>
                                <input type="text" class="form-control" v-model="profile.industry" required>
                            </div>

                            <div class="mb-3">
                                <label class="font-weight-bold">Website URL</label>
                                <input type="url" class="form-control" v-model="profile.website" required>
                            </div>

                            <div class="mb-3">
                                <label class="font-weight-bold">Location</label>
                                <input type="text" class="form-control" v-model="profile.location" required>
                            </div>

                            <div class="text-end">
                                <button type="submit" class="btn btn-primary btn-block">Update Profile</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!--  Created Placement Drives -->
            <div class="card p-4 mb-5 shadow-sm bg-white border-0">
                <h3 class="mb-3 text-dark">Your Placement Drives</h3>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover align-middle">
                        <thead class="table-dark">
                            <tr>
                                <th>Drive ID</th>
                                <th>Job Title</th>
                                <th>Salary Package</th>
                                <th>CGPA Cutoff</th>
                                <th>Deadline</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="drive in drives" :key="drive.id">
                                <td>Drive {{ drive.id }}</td>
                                <td class="font-weight-bold text-primary">{{ drive.job_title }}</td>
                                <td>{{ drive.salary_package }}</td>
                                <td>CGPA >= {{ drive.min_cgpa_criteria }}</td>
                                <td>{{ drive.application_deadline }}</td>
                                <td>
                                    <span class="badge" :class="{
                                        'bg-success': drive.drive_status === 'approved',
                                        'bg-primary': drive.drive_status === 'pending',
                                        'bg-danger': drive.drive_status === 'closed',
                                    }">{{ drive.drive_status }}</span>
                                </td>
                                <td>
                                    <button @click="viewDriveDetails(drive)" class="btn btn-sm btn-primary me-2">View
                                        Drive</button>
                                    <!-- Only allow closing if it is not already closed -->
                                    <button v-if="drive.drive_status !== 'closed'" @click="closeDrive(drive.id)"
                                        class="btn btn-sm btn-outline-danger ">Close Position</button>
                                    <span v-else class="text-muted small">No actions</span>
                                </td>
                            </tr>
                            <tr v-if="drives.length === 0">
                                <td colspan="7" class="text-center text-muted py-3">You have not created any Placement
                                    Drives yet.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!--  View Drive Details -->
            <div v-if="selectedDrive" class="modal-backdrop d-flex align-items-center justify-content-center">
                <div class="card p-4 shadow-lg bg-white" style="max-width: 600px; width: 100%;">
                    <div class="border-bottom pb-2 mb-3">
                        <h2 class="m-0 text-primary">Drive Details: Drive {{ selectedDrive.id }}</h2>
                    </div>
                    <div class="mb-3 text-left">
                        <p><strong>Job Title:</strong> {{ selectedDrive.job_title }}</p>
                        <p><strong>Job Description:</strong> {{ selectedDrive.job_description }}</p>
                        <p><strong>Salary (Package Details):</strong> {{ selectedDrive.salary_package }}</p>
                        <p><strong>Minimum CGPA Cutoff:</strong> {{ selectedDrive.min_cgpa_criteria }}</p>
                        <p><strong>Application Deadline:</strong> {{ selectedDrive.application_deadline }}</p>
                        <p><strong>Drive Status:</strong>
                            <span class="badge ml-1" :class="{
                                'bg-success': selectedDrive.drive_status === 'approved',
                                'bg-primary': selectedDrive.drive_status === 'pending',
                                'bg-danger': selectedDrive.drive_status === 'closed'
                            }">{{ selectedDrive.drive_status }}</span>
                        </p>
                    </div>
                    <div class="text-right">
                        <button @click="selectedDrive = null" class="btn btn-secondary">Close</button>
                    </div>
                </div>
            </div>

            <!--  Received Student Applications -->
            <div class="card p-4 mb-5 shadow-sm bg-white border-0">
                <h3 class="mb-3 text-dark">Received Applications</h3>
                <div class="table-responsive">
                    <table class="table table-bordered table-hover align-middle text-center">
                        <thead class="table-dark">
                            <tr>
                                <th>App ID</th>
                                <th>Applicant Name</th>
                                <th>Roll No</th>
                                <th>CGPA</th>
                                <th>Department</th>
                                <th>Job Position</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="application in applications" :key="application.id">
                                <td>{{ application.id }}</td>
                                <td class="font-weight-bold">{{ application.student_name }}</td>
                                <td>{{ application.roll_no }}</td>
                                <td>{{ application.cgpa }}</td>
                                <td>{{ application.department }}</td>
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
                                    <a :href="'http://localhost:5000/static/uploads/resumes/' + application.resume_link"
                                        class="btn btn-xs btn-outline-info me-2" target="_blank">View Resume</a>

                                    <!-- Action Buttons to update status -->
                                    <button v-if="application.status === 'applied'"
                                        @click="updateAppStatus(application.id, 'shortlisted')"
                                        class="btn btn-xs btn-warning me-2">Shortlist
                                    </button>
                                    <button v-if="application.status === 'shortlisted'"
                                        @click="updateAppStatus(application.id, 'interview')"
                                        class="btn btn-xs btn-info text-white me-2">Schedule Interview
                                    </button>
                                    <button v-if="application.status === 'interview'"
                                        @click="initiateOfferForm(application)"
                                        class="btn btn-xs btn-success me-2">Issue Offer
                                    </button>
                                    <button
                                        v-if="application.status !== 'rejected' && application.status !== 'selected' && application.status !== 'placed' && application.status !== 'offer'"
                                        @click="updateAppStatus(application.id, 'rejected')"
                                        class="btn btn-xs btn-danger">Reject
                                    </button>
                                </td>

                            </tr>
                            <tr v-if="applications.length === 0">
                                <td colspan="8" class="text-center text-muted py-3">No applications submitted for your
                                    drive post yet.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Issue job offer-->
            <div v-if="offerForm.isActive" class="modal-backdrop d-flex align-items-center justify-content-center">
                <div class="card p-4 shadow-lg bg-white" style="max-width: 500px; width: 100%;">
                    <div class="border-bottom pb-2 mb-3">
                        <h3 class="m-0 text-success">Send Job Offer</h3>
                    </div>
                    <form @submit.prevent="submitJobOffer">
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Name</label>
                            <input type="text" class="form-control" :value="offerForm.studentName" disabled />
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Position</label>
                            <input type="text" class="form-control" v-model="offerForm.position" required />
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Joining Date</label>
                            <input type="date" class="form-control" v-model="offerForm.joiningDate" required />
                        </div>
                        <div class="mb-3">
                            <label class="form-label font-weight-bold">Offer Letter(PDF)</label>
                            <input type="file" class="form-control" @change="onOfferLetterSelected" accept=".pdf"
                                required />
                        </div>
                        <div class="text-end">
                            <button type="button" @click="offerForm.isActive = false"
                                class="btn btn-secondary me-2">Cancel</button>
                            <button type="submit" class="btn btn-success">Issue Offer</button>
                        </div>
                    </form>
                </div>
            </div>

        </div>
    </div>

</template>

<script>
import axios from "axios"

export default {
    name: "CompanyDashboard",
    data() {
        return {
            profileStatus: "pending",
            profile: { id: null, name: "", industry: "", website: "", location: "" },
            stats: { total_drives: 0, total_applications: 0, total_shortlisted: 0 },
            drives: [],
            applications: [],

            // Create placement drive
            jobForm: {
                job_title: "",
                job_description: "",
                salary_package: "",
                min_cgpa_criteria: 0.0,
                application_deadline: ""
            },

            offerForm: {
                isActive: false,
                appId: null,
                studentName: "",
                position: "",
                joiningDate: "",
                file: null
            },

            selectedDrive: null,
            alertMessage: "",
            headers: {}
        }
    },

    methods: {
        setHeaders() {
            const token = localStorage.getItem("token")
            this.headers = { headers: { "Authentication-Token": token } }
        },

        async checkProfileStatus() {
            this.setHeaders()
            try {
                const res = await axios.get("http://localhost:5000/company/profile", this.headers)
                this.profile = res.data
                this.profileStatus = res.data.status

                // If approved, load the dashboard statistics and lists
                if (this.profileStatus === "approved") {
                    this.fetchDashboardData()
                }
            }
            catch (err) {
                console.error("Failed to load company profile.", err)
            }
        },

        async fetchDashboardData() {
            try {
                const statsRes = await axios.get("http://localhost:5000/company/statistics", this.headers)
                this.stats = statsRes.data

                const drivesRes = await axios.get("http://localhost:5000/company/drives", this.headers)
                this.drives = drivesRes.data

                const appsRes = await axios.get("http://localhost:5000/company/applications", this.headers)
                this.applications = appsRes.data
            }
            catch (err) {
                console.error("Failed to load dashboard parameters.", err)
            }
        },

        async updateProfile() {
            try {
                await axios.put("http://localhost:5000/company/profile", this.profile, this.headers)
                this.alertMessage = "Company profile details updated successfully."
                this.checkProfileStatus()
            }
            catch (err) {
                console.error(err)
            }
        },

        async createPlacementDrive() {
            try {
                const res = await axios.post("http://localhost:5000/company/drives", this.jobForm, this.headers)
                this.alertMessage = res.data.message

                // Reset job form values
                this.jobForm = { job_title: "", job_description: "", salary_package: "", min_cgpa_criteria: 0.0, application_deadline: "" }

                this.fetchDashboardData()
            }
            catch (err) {
                this.alertMessage = err.response?.data?.message || "Failed to create placement drive."
            }
        },

        async closeDrive(id) {
            if (!confirm("Are you sure you want to close this placement drive?")) return
            try {
                const res = await axios.put(`http://localhost:5000/company/drive/${id}/close`, {}, this.headers)
                this.alertMessage = res.data.message
                this.fetchDashboardData()
            }
            catch (err) {
                console.error(err)
            }
        },

        async updateAppStatus(appId, status) {
            try {
                const res = await axios.put(`http://localhost:5000/company/application/${appId}/status`, { status }, this.headers)
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

        initiateOfferForm(application) {
            this.offerForm.appId = application.id;
            this.offerForm.studentName = application.student_name;
            this.offerForm.position = application.job_title;
            this.offerForm.joiningDate = "";
            this.offerForm.file = null;
            this.offerForm.isActive = true;
        },
        onOfferLetterSelected(event) {
            this.offerForm.file = event.target.files[0];
        },
        
        async submitJobOffer() {
            if (!this.offerForm.file) return;

            const payload = new FormData();
            payload.append("position", this.offerForm.position);
            payload.append("joining_date", this.offerForm.joiningDate);
            payload.append("offer_letter", this.offerForm.file);

            try {
                const token = localStorage.getItem("token");
                const res = await axios.post(
                    `http://localhost:5000/company/application/${this.offerForm.appId}/offer`,
                    payload,
                    {
                        headers: {
                            "Authentication-Token": token,
                            "Content-Type": "multipart/form-data"
                        }
                    }
                );
                this.alertMessage = res.data.message;
                this.offerForm.isActive = false;
                this.fetchDashboardData();
            } 
            catch (err) {
                this.alertMessage = err.response?.data?.message || "Failed to process job offer.";
            }
        }
    },
    created() {
        this.checkProfileStatus()
    }
}
</script>

<style scoped>
.btn-xs {
    padding: 4px 8px;
    font-size: 12px;
    border-radius: 4px;
}

.card {
    border-radius: 8px;
    overflow: hidden;
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