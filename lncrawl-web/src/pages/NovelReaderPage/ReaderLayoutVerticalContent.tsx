import cx from 'classnames';
import styles from './ReaderLayoutVertical.module.scss';

import { store } from '@/store';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { getVoices } from '../SettingsPage/ReaderSettings/VoiceSettings';

function useSpeechSynthesis(
  contentRef: React.RefObject<HTMLDivElement | null>,
  nextChapterId?: string
) {
  const navigate = useNavigate();

  const voiceUri = useSelector(Reader.select.voice);
  const speaking = useSelector(Reader.select.speaking);
  const position = useSelector(Reader.select.speakPosition);

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
      },
      { signal: aborter.signal }
    );
    return () => aborter.abort();
  }, []);

  useEffect(() => {
    if (!speaking || !voice || loading) return;

    const el = contentRef.current;
    if (!el) return;

    if (position >= el.children.length && nextChapterId) {
      navigate(`/read/${nextChapterId}`);
      return;
    }

    const node = el.children[position];

    const text = node.textContent;
    if (!text?.length) {
      store.dispatch(Reader.action.setSepakPosition(position + 1));
      return;
    }

    node.setAttribute('data-speak', 'true');
    // node.scrollIntoView({ behavior: 'smooth', block: 'center' });

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = voice;
    utterance.addEventListener('end', () => {
      node.removeAttribute('data-speak');
      store.dispatch(Reader.action.setSepakPosition(position + 1));
    });

    const tid = setTimeout(() => {
      window.speechSynthesis.speak(utterance);
    }, 50);

    return () => {
      clearTimeout(tid);
      window.speechSynthesis.cancel();
    };
  }, [speaking, voice, position, loading, nextChapterId]);
}

export const ReaderVerticalContent: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const contentRef = useRef<HTMLDivElement | null>(null);
  const speaking = useSelector(Reader.select.speaking);

  const contentHtml = useMemo(() => data.content || '', [data.content]);

  useSpeechSynthesis(contentRef, data.next_id);

  const handleClick = (e: React.MouseEvent<HTMLElement>) => {
    let target = e.target as HTMLElement | null;
    const el = contentRef.current;
    if (!el || !el.contains(target)) return;
    while (target && target.parentElement !== el) {
      target = target.parentElement!;
    }
    if (target) {
      const index = Array.prototype.indexOf.call(el.children, target);
      store.dispatch(Reader.action.setSepakPosition(index));
    }
  };

  return (
    <div
      ref={contentRef}
      dangerouslySetInnerHTML={{
        __html: contentHtml,
      }}
      onPointerUp={handleClick}
      className={cx(styles.content, {
        [styles.speaking]: speaking,
      })}
    />
  );
};
