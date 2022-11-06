export const makeToast = function(message, variant, title = "Notification") {
    this.$root.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: variant
    });
};

export const handleError = function(error) {
    if (error.response.status === 422 || error.response.status === 401) {
        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("refresh_token");
        this.$router.push({ name: "Login" });
    } else {
        const content = error.response.data.detail || error.response.data.msg;
        const title = error.response.data.status || "Notification";

        this.makeToast(content, "danger", title);
    }
};
