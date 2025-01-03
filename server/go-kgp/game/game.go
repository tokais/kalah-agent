// Game Model
//
// Copyright (c) 2021, 2022, 2023  Philip Kaludercic
//
// This file is part of go-kgp.
//
// go-kgp is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License,
// version 3, as published by the Free Software Foundation.
//
// go-kgp is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public
// License, version 3, along with go-kgp. If not, see
// <http://www.gnu.org/licenses/>

package game

import (
	"context"

	"go-kgp"
	"go-kgp/cmd"
)

func Move(g *kgp.Game, m *kgp.Move) bool {
	if !g.Board.Legal(g.Current, m.Choice) {
		return false
	}

	repeat := g.Board.Sow(g.Current, m.Choice)
	if !repeat {
		g.Current = !g.Current
	}
	return true
}

func MoveCopy(g *kgp.Game, m *kgp.Move) (*kgp.Game, bool) {
	c := &kgp.Game{
		Board:   g.Board.Copy(),
		South:   g.South,
		North:   g.North,
		Current: g.Current,
	}
	return c, Move(c, m)
}

func Play(g *kgp.Game, st *cmd.State, conf *cmd.Conf) error {
	dbg := kgp.Debug.Printf
	bg := context.Background()

	dbg("Starting game between %s and %s", g.South, g.North)

	g.State = kgp.ONGOING
	err := st.Database.SaveGame(bg, g)
	if err != nil {
		dbg("Failed to save game, skipping: %s", err)
		return err
	}
	for !g.Board.Over() {
		var m *kgp.Move

		count, last := g.Board.Moves(g.Current)
		dbg("Game %d: %s has %d moves",
			g.Id, g.State.String(), count)
		switch count {
		case 0:
			// If this happens, then Board.Over or
			// Board.Moves must be broken.
			panic("No moves even though game is not over")
		case 1:
			// Skip trivial moves
			m = &kgp.Move{
				Agent:   g.Active(),
				Comment: "[Auto-move]",
				Choice:  last,
				Game:    g,
			}
		default:
			var resign bool
			m, resign = g.Active().Request(g)
			if resign {
				dbg("Game %d: %s resigned", g.Id, g.Current)

				switch g.Current {
				case kgp.South:
					g.State = kgp.SOUTH_RESIGNED
				case kgp.North:
					g.State = kgp.NORTH_RESIGNED
				}

				goto save
			}
		}
		dbg("Game %d: %s made the move %d (%s)",
			g.Id, g.State.String(), m.Choice, m.Comment)

		side := g.Current
		if !Move(g, m) {
			dbg("Game %d: %s made illegal move %d",
				g.Id, g.Current, m.Choice)

			switch side {
			case kgp.South:
				g.State = kgp.SOUTH_RESIGNED
			case kgp.North:
				g.State = kgp.NORTH_RESIGNED
			}
			goto save
		}

		// Save the move in the database, and take as much
		// time as necessary.
		err := st.Database.SaveMove(bg, m)
		if err != nil {
			dbg("Failed to save move: %s", err)
		} else {
			// dbg("Game %d: %s", g.Id, g.State.String())
		}
	}

	switch g.Board.Outcome(kgp.South) {
	case kgp.WIN, kgp.LOSS:
		if g.Board.Store(kgp.North) > g.Board.Store(kgp.South) {
			g.State = kgp.NORTH_WON
		} else {
			g.State = kgp.SOUTH_WON
		}
	case kgp.DRAW:
		g.State = kgp.UNDECIDED
	}
save:
	err = st.Database.SaveGame(bg, g)
	if err != nil {
		dbg("Failed to save final game state: %s", err)
		return err
	}
	kgp.Debug.Printf("Game %d finished (%s)", g.Id, &g.State)
	return nil
}
