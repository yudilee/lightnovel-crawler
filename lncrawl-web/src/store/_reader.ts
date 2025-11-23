import { FontFamily, ReaderLayout, ReaderTheme } from '@/types';
import type { PayloadAction } from '@reduxjs/toolkit';
import { createSelector, createSlice } from '@reduxjs/toolkit';
import type { PersistConfig } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import type { RootState } from '.';

//
// Initial State
//

export interface ReaderState {
  voice: string | undefined;
  speaking: boolean;
  speakPosition: number;
  fontSize: number;
  lineHeight: number;
  theme: ReaderTheme;
  layout: ReaderLayout;
  fontFamily: FontFamily;
}

const buildInitialState = (): ReaderState => ({
  layout: ReaderLayout.vertical,
  speaking: false,
  speakPosition: 0,
  voice: undefined,
  fontSize: 16,
  lineHeight: 1.4,
  theme: ReaderTheme.Dark,
  fontFamily: FontFamily.Literata,
});

//
// Slice
//
export const ReaderSlice = createSlice({
  name: 'reader',
  initialState: buildInitialState(),
  reducers: {
    setLayout(state, action: PayloadAction<ReaderState['layout']>) {
      state.layout = action.payload;
    },
    setVoice(state, action: PayloadAction<ReaderState['voice']>) {
      state.voice = action.payload;
    },
    setTheme(state, action: PayloadAction<ReaderState['theme']>) {
      state.theme = action.payload;
    },
    setLineHeight(state, action: PayloadAction<ReaderState['lineHeight']>) {
      state.lineHeight = action.payload;
    },
    setFontSize(state, action: PayloadAction<ReaderState['fontSize']>) {
      state.fontSize = action.payload;
    },
    setFontFamily(state, action: PayloadAction<ReaderState['fontFamily']>) {
      state.fontFamily = action.payload;
    },
    setSpeaking(state, action: PayloadAction<ReaderState['speaking']>) {
      state.speaking = action.payload;
    },
    setSepakPosition(state, action: PayloadAction<number>) {
      state.speakPosition = action.payload;
    },
  },
});

//
// Actions & Selectors
//
const selectReader = (state: RootState) => state.reader;

export const Reader = {
  action: ReaderSlice.actions,
  select: {
    theme: createSelector(selectReader, (reader) => reader.theme),
    layout: createSelector(selectReader, (reader) => reader.layout),
    fontSize: createSelector(selectReader, (reader) => reader.fontSize),
    fontFamily: createSelector(selectReader, (reader) => reader.fontFamily),
    lineHeight: createSelector(selectReader, (reader) => reader.lineHeight),
    voice: createSelector(selectReader, (reader) => reader.voice),
    speaking: createSelector(selectReader, (reader) => reader.speaking),
    speakPosition: createSelector(
      selectReader,
      (reader) => reader.speakPosition
    ),
  },
};

//
// Persist Config
//
const blacklist: Array<keyof ReaderState> = [
  // items to exclude from local storage
  'speaking',
  'speakPosition',
];

export const readerPersistConfig: PersistConfig<ReaderState> = {
  key: 'reader',
  version: 1,
  storage,
  blacklist,
};
