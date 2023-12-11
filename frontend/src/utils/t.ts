export function convertToMilliseconds(timeString: string) {
  // 00:00:00.001 -> 1
  // 00:00:00.100 -> 100
  // 00:00:01.000 -> 6000
  // Split the time string into hours, minutes, seconds and milliseconds
  const [hours, minutes, seconds] = timeString.split(":")
  const [mainSeconds, milliseconds] = seconds.split(".")

  // Convert each unit to milliseconds and add them up
  const hoursInMs = Number(hours) * 60 * 60 * 1000
  const minutesInMs = Number(minutes) * 60 * 1000
  const secondsInMs = Number(mainSeconds) * 1000
  return hoursInMs + minutesInMs + secondsInMs + Number(milliseconds)
}

export function convertToTimeString(ms: number) {
  // Calculate hours, minutes, seconds and milliseconds from the total milliseconds
  const hours = Math.floor(ms / (60 * 60 * 1000))
  const minutes = Math.floor((ms % (60 * 60 * 1000)) / (60 * 1000))
  const seconds = Math.floor((ms % (60 * 1000)) / 1000)
  const milliseconds = ms % 1000

  // Format hours, minutes, seconds and milliseconds as two-digit strings
  const hoursStr = hours.toString().padStart(2, "0")
  const minutesStr = minutes.toString().padStart(2, "0")
  const secondsStr = seconds.toString().padStart(2, "0")
  const millisecondsStr = milliseconds.toString().padStart(3, "0")

  // Combine the parts into a single time string
  return `${hoursStr}:${minutesStr}:${secondsStr}.${millisecondsStr}`
}

export const ensureSpaceAfterComma = (text) => {
  let newText = text.replace(/,\s*/g, ",")
  newText = newText.replace(/,/g, ", ")
  return newText
}
