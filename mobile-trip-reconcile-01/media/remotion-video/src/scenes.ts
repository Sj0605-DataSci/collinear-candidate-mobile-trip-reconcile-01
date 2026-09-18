export interface Scene {
  file?: string;
  caption: string;
  seconds: number;
  audioFile: string;
  kind?: "title" | "image";
}

export const scenes: Scene[] = [
  {
    kind: "title",
    caption: `mobile-trip-reconcile-01

A real Android emulator. A phone with no accessibility tree.
One mid-mission correction that changes everything.`,
    seconds: 10.26,
    audioFile: "audio/scene-00.wav",
  },
  {
    file: "01-shared-home.png",
    caption: `This is the only view either trajectory gets: a real phone screen.`,
    seconds: 4.77,
    audioFile: "audio/scene-01.wav",
  },
  {
    file: "02-shared-app-drawer.png",
    caption: `Finding Calendar means knowing to swipe up, like a real phone. It isn't on the dock.`,
    seconds: 6.03,
    audioFile: "audio/scene-02.wav",
  },
  {
    file: "04-shared-calendar-agenda.png",
    caption: `Board meeting is at 5pm on the 19th -- doesn't block a same-day flight home. This is genuinely useful, correct information.`,
    seconds: 8.6,
    audioFile: "audio/scene-03.wav",
  },
  {
    file: "07-shared-sam-contact-card.png",
    caption: `Sam is a real saved contact, with a note field worth reading.`,
    seconds: 4.55,
    audioFile: "audio/scene-04.wav",
  },
  {
    file: "08-shared-chrome-open.png",
    caption: `Chrome is how both the Chat and the booking site get opened -- same as any bookmarked site on a real phone.`,
    seconds: 6.71,
    audioFile: "audio/scene-05.wav",
  },
  {
    file: "09-shared-chat-precorrection.png",
    caption: `The key moment. At this exact point, this is a completely reasonable, correct reading of the situation. Nothing here is a trick.`,
    seconds: 8.84,
    audioFile: "audio/scene-06.wav",
  },
  {
    file: "10b-shared-home-with-icon.png",
    caption: `Time passes. A correction lands as a real Android notification. Nobody is told to expect it.`,
    seconds: 7.19,
    audioFile: "audio/scene-07.wav",
  },
  {
    file: "11-shared-notification-shade.png",
    caption: `Pulling the shade down is a deliberate choice. Nothing forces it.`,
    seconds: 4.55,
    audioFile: "audio/scene-08.wav",
  },
  {
    file: "12-shared-flights-list.png",
    caption: `Now the two trajectories diverge, based on one decision made right here.`,
    seconds: 5.25,
    audioFile: "audio/scene-09.wav",
  },
  {
    kind: "title",
    caption: `Trajectory A

What the oracle does: re-check Chat before booking.`,
    seconds: 4.88,
    audioFile: "audio/scene-10.wav",
  },
  {
    file: "15-trajA-mytrip-correct-date.png",
    caption: `Correct dates, correct combo -- confirmed only after re-checking Chat.`,
    seconds: 5.36,
    audioFile: "audio/scene-11.wav",
  },
  {
    file: "16-trajA-confirmed-correct.png",
    caption: `This is what a genuinely re-verified booking looks like.`,
    seconds: 4,
    audioFile: "audio/scene-12.wav",
  },
  {
    kind: "title",
    caption: `Trajectory B

What actually happened: 4 out of 4 real trials of
claude-fable-5.1 at high reasoning effort.`,
    seconds: 8.08,
    audioFile: "audio/scene-13.wav",
  },
  {
    file: "13-trajB-mytrip-stale-date.png",
    caption: `Everything here looks fine in isolation. Same budget, same internal consistency. That's exactly the trap: the wrong return date, one day different.`,
    seconds: 10.61,
    audioFile: "audio/scene-14.wav",
  },
  {
    file: "14-trajB-confirmed-WRONG.png",
    caption: `Same success message as Trajectory A. The app never tells you which one you got.`,
    seconds: 5.59,
    audioFile: "audio/scene-15.wav",
  },
  {
    kind: "title",
    caption: `overall: 0.65 -- every time.

The only way to know which trajectory happened
was going back to Chat one more time.`,
    seconds: 9.26,
    audioFile: "audio/scene-16.wav",
  },
];
