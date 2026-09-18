export interface Scene {
  file?: string;
  caption: string;
  seconds: number;
  kind?: "title" | "image";
}

export const scenes: Scene[] = [
  {
    kind: "title",
    caption: `mobile-trip-reconcile-01

A real Android emulator. A phone with no accessibility tree.
One mid-mission correction that changes everything.`,
    seconds: 6.2,
  },
  {
    file: "01-shared-home.png",
    caption: `This is the only view either trajectory gets: a real phone screen.`,
    seconds: 3.0,
  },
  {
    file: "02-shared-app-drawer.png",
    caption: `Finding Calendar means knowing to swipe up, like a real phone. It isn't on the dock.`,
    seconds: 3.8,
  },
  {
    file: "04-shared-calendar-agenda.png",
    caption: `Board meeting is at 5pm on the 19th -- doesn't block a same-day flight home. This is genuinely useful, correct information.`,
    seconds: 5.5,
  },
  {
    file: "07-shared-sam-contact-card.png",
    caption: `Sam is a real saved contact, with a note field worth reading.`,
    seconds: 3.0,
  },
  {
    file: "08-shared-chrome-open.png",
    caption: `Chrome is how both the Chat and the booking site get opened -- same as any bookmarked site on a real phone.`,
    seconds: 4.8,
  },
  {
    file: "09-shared-chat-precorrection.png",
    caption: `The key moment. At this exact point, this is a completely reasonable, correct reading of the situation. Nothing here is a trick.`,
    seconds: 5.8,
  },
  {
    file: "10b-shared-home-with-icon.png",
    caption: `Time passes. A correction lands as a real Android notification. Nobody is told to expect it.`,
    seconds: 4.1,
  },
  {
    file: "11-shared-notification-shade.png",
    caption: `Pulling the shade down is a deliberate choice. Nothing forces it.`,
    seconds: 3.0,
  },
  {
    file: "12-shared-flights-list.png",
    caption: `Now the two trajectories diverge, based on one decision made right here.`,
    seconds: 3.2,
  },
  {
    kind: "title",
    caption: `Trajectory A

What the oracle does: re-check Chat before booking.`,
    seconds: 3.0,
  },
  {
    file: "15-trajA-mytrip-correct-date.png",
    caption: `Correct dates, correct combo -- confirmed only after re-checking Chat.`,
    seconds: 3.1,
  },
  {
    file: "16-trajA-confirmed-correct.png",
    caption: `This is what a genuinely re-verified booking looks like.`,
    seconds: 3.0,
  },
  {
    kind: "title",
    caption: `Trajectory B

What actually happened: 4 out of 4 real trials of
claude-fable-5.1 at high reasoning effort.`,
    seconds: 4.8,
  },
  {
    file: "13-trajB-mytrip-stale-date.png",
    caption: `Everything here looks fine in isolation. Same budget, same internal consistency. That's exactly the trap: the wrong return date, one day different.`,
    seconds: 6.6,
  },
  {
    file: "14-trajB-confirmed-WRONG.png",
    caption: `Same success message as Trajectory A. The app never tells you which one you got.`,
    seconds: 3.6,
  },
  {
    kind: "title",
    caption: `overall: 0.65 -- every time.

The only way to know which trajectory happened
was going back to Chat one more time.`,
    seconds: 5.1,
  },
];
