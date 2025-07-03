export const makeToast = function (message, variant, title = "Notification") {
  this.$root.$bvToast.toast(message, {
    title: title,
    autoHideDelay: 3000,
    appendToast: false,
    variant: variant,
    toaster: "b-toaster-bottom-right",
  });
};

export const handleError = function (error) {
  if (error.response.status === 422 || error.response.status === 401) {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
    this.$router.push({ name: "Login" });
  } else {
    let content = "";
    if (error.response.data.validation_error) {
      content = `${error.response.data.validation_error.body_params[0].loc[0]}: ${error.response.data.validation_error.body_params[0].msg}`;
    } else {
      content = error.response.data.detail || error.response.data.msg;
    }

    const title = error.response.data.status || "Notification";

    this.makeToast(content, "danger", title);
  }
};
