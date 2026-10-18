import {Composition} from 'remotion';
import {Kinetic} from './Kinetic';

// Edit WORDS below, then: npm install && npx remotion render Kinetic out.mp4
export const RemotionRoot = () => (
  <Composition
    id="Kinetic"
    component={Kinetic}
    durationInFrames={300}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{words: ['THIS', 'CAR', 'FLIES']}}
  />
);
