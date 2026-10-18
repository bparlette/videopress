import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// Per-word punch-in kinetic typography. Each word slams in with a spring,
// holds, then the next word takes over. Drop your words in via defaultProps.
export const Kinetic = ({words}: {words: string[]}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const perWord = 45; // frames per word

  const idx = Math.min(Math.floor(frame / perWord), words.length - 1);
  const local = frame - idx * perWord;

  const scale = spring({frame: local, fps, config: {damping: 12, stiffness: 200}});
  const opacity = interpolate(local, [0, 6], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#0a0a0a', justifyContent: 'center', alignItems: 'center'}}>
      <div style={{
        fontSize: 120, fontWeight: 900, color: '#ffd928',
        transform: `scale(${scale})`, opacity,
        textShadow: '6px 6px 0 #000',
        fontFamily: 'Arial Black, sans-serif', textAlign: 'center', padding: 40,
      }}>
        {words[idx]}
      </div>
    </AbsoluteFill>
  );
};
