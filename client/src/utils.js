export const makeToast = function (message, variant, title) {
    this.$root.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: false,
        variant: variant,
    });
}

export const handleError = function (error) {
    if (error.response.status === 422 || error.response.status === 401) {
        sessionStorage.removeItem("access_token");
        sessionStorage.removeItem("refresh_token");
        this.$router.push({ name: "Login" });
    } else {
        this.makeToast(
            error.response.data.detail,
            "danger",
            error.response.data.status
        );
    }
}
