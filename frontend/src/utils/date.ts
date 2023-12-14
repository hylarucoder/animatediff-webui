// Date utilities
export function getUtcNow() {
  return new Date().toISOString().toString()
}

export function formatDateString(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()

  const timeDifference = now.getTime() - date.getTime()
  const withinOneDay = timeDifference < 24 * 60 * 60 * 1000
  const withinOneYear = now.getFullYear() - date.getFullYear() < 1

  const hours = date.getHours().toString().padStart(2, "0")
  const minutes = date.getMinutes().toString().padStart(2, "0")
  const day = date.getDate().toString().padStart(2, "0")
  const month = (date.getMonth() + 1).toString().padStart(2, "0")
  const year = date.getFullYear()

  if (withinOneDay) {
    return `${hours}:${minutes}`
  } else if (withinOneYear) {
    return `${month}/${day} ${hours}:${minutes}`
  } else {
    return `${year}/${month}/${day}`
  }
}

export const formatDurationHHMMSS = (duration: number): string => {
  const hours = Math.floor(duration / 3600)
  const minutes = Math.floor((duration % 3600) / 60)
  const seconds = duration % 60

  // Pad the minutes and seconds with leading zeros, if required
  const paddedHours = hours.toString().padStart(2, "0")
  const paddedMinutes = minutes.toString().padStart(2, "0")
  const formattedSeconds = seconds < 10 ? "0" + seconds.toFixed(3) : seconds.toFixed(3)

  return `${paddedHours}:${paddedMinutes}:${formattedSeconds}`
}
