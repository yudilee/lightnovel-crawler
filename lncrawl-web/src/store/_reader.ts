import { FontFamily, ReaderTheme } from '@/types';
import type { PayloadAction } from '@reduxjs/toolkit';
import { createSelector, createSlice } from '@reduxjs/toolkit';
import type { PersistConfig } from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import type { RootState } from '.';

//
// Initial State
//

export interface ReaderState {
  fontSize: number;
  lineHeight: number;
  theme: ReaderTheme;
  fontFamily: FontFamily;
}

const buildInitialState = (): ReaderState => ({
  fontSize: 18,
  lineHeight: 1.25,
  theme: ReaderTheme.Dark,
  fontFamily: FontFamily.ArbutusSlab,
});

//
// Slice
//
export const ReaderSlice = createSlice({
  name: 'reader',
  initialState: buildInitialState(),
  reducers: {
    setColor(state, action: PayloadAction<ReaderTheme>) {
      state.theme = action.payload;
    },
    setLineHeight(state, action: PayloadAction<number>) {
      state.lineHeight = action.payload;
    },
    setFontSize(state, action: PayloadAction<number>) {
      state.fontSize = action.payload;
    },
    setFontFamily(state, action: PayloadAction<FontFamily>) {
      state.fontFamily = action.payload;
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
    fontSize: createSelector(selectReader, (reader) => reader.fontSize),
    fontFamily: createSelector(selectReader, (reader) => reader.fontFamily),
    lineHeight: createSelector(selectReader, (reader) => reader.lineHeight),
  },
};

//
// Persist Config
//
const blacklist: Array<keyof ReaderState> = [
  // items to exclude from local storage
];

export const readerPersistConfig: PersistConfig<ReaderState> = {
  key: 'reader',
  version: 1,
  storage,
  blacklist,
};
