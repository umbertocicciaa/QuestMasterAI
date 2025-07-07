(define (domain simple-adventure)
  (:requirements :strips :typing)
  (:types location)

  (:predicates
    (at ?loc - location)
    (has_treasure)
  )

  ;; Azioni per muoversi tra location
  (:action go_hut
    :precondition (at start)
    :effect (and (not (at start)) (at hut))
  )

  (:action go_cave_from_start
    :precondition (at start)
    :effect (and (not (at start)) (at cave))
  )

  (:action follow_map
    :precondition (at hut)
    :effect (and (not (at hut)) (at cave))
  )

  (:action fight_serpent
    :precondition (at cave)
    :effect (and (not (at cave)) (at fight))
  )

  (:action open_chest
    :precondition (at fight)
    :effect (has_treasure)
  )

  (:action flee_cave
    :precondition (at cave)
    :effect (and (not (at cave)) (at beach_end))
  )
)
