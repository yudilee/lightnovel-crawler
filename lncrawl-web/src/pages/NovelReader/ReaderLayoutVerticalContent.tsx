import cx from 'classnames';
import styles from './ReaderLayoutVertical.module.scss';

import { store } from '@/store';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { getVoices } from '../SettingsPage/ReaderSettings/VoiceSettings';
import { ReaderSpeakNavVar } from './ReaderSpeakNavBar';

function useSpeechSynthesis(
  contentEl: HTMLDivElement | null,
  data: ReadChapter
) {
  const navigate = useNavigate();

  const voiceUri = useSelector(Reader.select.voice);
  const speaking = useSelector(Reader.select.speaking);
  const position = useSelector(Reader.select.speakPosition);
  const voiceSpeed = useSelector(Reader.select.voiceSpeed);
  const voicePitch = useSelector(Reader.select.voicePitch);

  const [loading, setLoading] = useState<boolean>(true);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

  const voice = useMemo(
    () => voices.find((x) => x.voiceURI === voiceUri) || voices[0],
    [voices, voiceUri]
  );

  useEffect(() => {
    getVoices()
      .then(setVoices)
      .finally(() => setLoading(false));

    const aborter = new AbortController();
    window.addEventListener(
      'beforeunload',
      () => {
        window.speechSynthesis.cancel();
        store.dispatch(Reader.action.setSpeaking(false));
      },
      { signal: aborter.signal }
    );
    return () => aborter.abort();
  }, []);

  useEffect(() => {
    if (!contentEl || !speaking) {
      return;
    }

    if (position >= contentEl.children.length) {
      store.dispatch(Reader.action.setSepakPosition(0));
      if (data.next_id) {
        navigate(`/read/${data.next_id}`);
      } else {
        store.dispatch(Reader.action.setSpeaking(false));
      }
      return;
    }

    const childEl = contentEl.children[position];

    const text = childEl.textContent;
    if (!text?.length) {
      store.dispatch(Reader.action.setSepakPosition(position + 1));
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.rate = voiceSpeed;
    utterance.pitch = voicePitch;

    utterance.addEventListener('end', () => {
      store.dispatch(Reader.action.setSepakPosition(position + 1));
    });

    const tid = setTimeout(() => {
      window.speechSynthesis.speak(utterance);
    }, 50);

    return () => {
      clearTimeout(tid);
      requestAnimationFrame(() => {
        window.speechSynthesis.cancel();
      });
    };
  }, [
    data,
    contentEl,
    speaking,
    voice,
    voiceSpeed,
    voicePitch,
    position,
    loading,
    navigate,
  ]);

  useEffect(() => {
    if (loading || !contentEl || !speaking || !voice || !data.content) {
      return;
    }

    if (position >= contentEl.children.length) {
      store.dispatch(Reader.action.setSepakPosition(0));
      if (data.next_id) {
        navigate(`/read/${data.next_id}`);
      } else {
        store.dispatch(Reader.action.setSpeaking(false));
      }
      return;
    }

    const childEl = contentEl.children[position];

    const text = childEl.textContent;
    if (!text?.length) {
      store.dispatch(Reader.action.setSepakPosition(position + 1));
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.rate = voiceSpeed;
    utterance.pitch = voicePitch;

    utterance.addEventListener('end', () => {
      store.dispatch(Reader.action.setSepakPosition(position + 1));
    });

    const tid = setTimeout(() => {
      window.speechSynthesis.speak(utterance);
    }, 50);

    return () => {
      clearTimeout(tid);
      requestAnimationFrame(() => {
        window.speechSynthesis.cancel();
      });
    };
  }, [
    data,
    contentEl,
    speaking,
    voice,
    voiceSpeed,
    voicePitch,
    position,
    loading,
    navigate,
  ]);
}

export const ReaderVerticalContent: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const speaking = useSelector(Reader.select.speaking);
  const position = useSelector(Reader.select.speakPosition);
  const [contentEl, setContentEl] = useState<HTMLDivElement | null>(null);

  useSpeechSynthesis(contentEl, data);

  const handleClick = (e: React.MouseEvent<HTMLElement>) => {
    let target = e.target as HTMLElement | null;
    if (!contentEl || !contentEl.contains(target)) return;
    while (target && target.parentElement !== contentEl) {
      target = target.parentElement!;
    }
    if (target) {
      const index = Array.prototype.indexOf.call(contentEl.children, target);
      store.dispatch(Reader.action.setSepakPosition(index));
    }
  };

  useEffect(() => {
    if (!speaking) return;
    const fid = requestAnimationFrame(() => {
      const childEl = contentEl?.children[position];
      childEl?.setAttribute('data-focus', 'true');
    });
    return () => {
      cancelAnimationFrame(fid);
      const childEl = contentEl?.children[position];
      childEl?.removeAttribute('data-focus');
    };
  });

  return (
    <>
      <div
        id="chapter-content"
        ref={setContentEl}
        dangerouslySetInnerHTML={{
          __html: data.content || '',
        }}
        onPointerUp={handleClick}
        className={cx(styles.content, {
          [styles.speaking]: speaking,
        })}
      />

      {speaking && <ReaderSpeakNavVar data={data} />}
    </>
  );
};
